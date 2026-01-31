#!/usr/bin/env python3
"""
Orchestrate skill evaluations across multiple providers/models.

Refactored for scalability following programming skills:
- Policy-Mechanism Separation: Config drives execution
- Composition Over Coordination: Small focused scripts combined
- Single Responsibility: Each script does one thing
- Explicit State Invariants: Configuration validated upfront
- Single Direction Data Flow: Clear pipeline of operations
"""

import subprocess
import sys
import os
import json
from pathlib import Path
import argparse


def validate_environment():
    """Validate required environment variables."""
    if not os.environ.get("GITHUB_TOKEN"):
        print("❌ Error: GITHUB_TOKEN not set")
        sys.exit(1)

    if not os.environ.get("OLLAMA_API_KEY"):
        print("⚠ Warning: OLLAMA_API_KEY not set (required for Ollama)")

    return True


def detect_changes(pr_number: int) -> str:
    """Detect modified skills in PR."""
    print("\n==> Detecting changes in PR #{}".format(pr_number))

    result = subprocess.run(
        ["python3", "ci/detect_changes.py", str(pr_number)],
        capture_output=True,
        text=True,
    )

    modified_skills = result.stdout.strip()

    if modified_skills:
        skill_list = modified_skills.split()
        print(f"✓ Found {len(skill_list)} modified skill(s): {', '.join(skill_list[:3])}" + 
              (f" +{len(skill_list)-3} more" if len(skill_list) > 3 else ""))
    else:
        print("✓ No skills modified - will test all skills")

    return modified_skills


def generate_matrix(filter_provider: str = "all", skills: str = "") -> list:
    """Generate evaluation matrix from configuration with per-skill jobs.
    
    If skills are provided, creates one matrix item per skill per model.
    Otherwise creates one item per model (tests all skills).
    """
    print("\n==> Generating evaluation matrix")

    result = subprocess.run(
        ["uv", "run", "--with", "pyyaml", "ci/matrix_generator.py", "--filter-provider", filter_provider],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("❌ Error generating matrix")
        print(result.stderr)
        sys.exit(1)

    try:
        matrix_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("❌ Error parsing matrix JSON")
        print(result.stdout)
        sys.exit(1)

    items = matrix_data.get("include", [])

    if not items:
        print("❌ Error: No enabled providers in configuration")
        sys.exit(1)

    # If skills are specified, expand matrix to one item per skill per model
    if skills and skills.strip():
        skill_list = skills.strip().split()
        expanded_items = []
        
        for item in items:
            for skill in skill_list:
                expanded_item = item.copy()
                expanded_item["skill"] = skill
                expanded_item["display_name"] = f"{item['display_name']} / {skill}"
                expanded_items.append(expanded_item)
        
        items = expanded_items
        print(f"✓ Generated matrix with {len(items)} job(s) ({len(items)//len(skill_list)} model(s) × {len(skill_list)} skill(s))")
    else:
        print(f"✓ Generated matrix with {len(items)} configuration(s) (all skills per model)")
    
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item['display_name']}")

    return items


def run_sequential(items: list, threshold: int = 50):
    """Run evaluations sequentially."""
    print("\n==> Running evaluations sequentially")

    for item in items:
        provider = item["provider"]
        model = item["model"]
        extra_args = item.get("extra_args", "")

        result = subprocess.run(
            ["python3", "ci/run_evaluation.py", provider, model, str(threshold), extra_args]
        )

        if result.returncode != 0:
            print(f"⚠ Evaluation failed for {provider}/{model}")

    print("✓ All evaluations completed")

    # Consolidate
    subprocess.run(["python3", "ci/consolidate_results.py"])


def run_parallel_local(items: list, threshold: int = 50):
    """Run evaluations in parallel locally (one job per skill per model)."""
    print(f"\n==> Running {len(items)} evaluation(s) in parallel")

    import concurrent.futures
    
    def run_single_eval(item):
        provider = item["provider"]
        model = item["model"]
        extra_args = item.get("extra_args", "")
        skill = item.get("skill")
        
        display = f"{provider}/{model}" + (f"/{skill}" if skill else "")
        print(f"[{display}] Starting...")
        
        cmd = [
            "uv",
            "run",
            "--project",
            "tests",
            "--frozen",
            "tests/evaluator.py",
            "--provider",
            provider,
            "--model",
            model,
            "--threshold",
            str(threshold),
            "--judge",
            "--verbose",
            "--report",
        ]
        
        if extra_args.strip():
            cmd.extend(extra_args.split())
        
        if skill:
            cmd.extend(["--skill", skill])
        else:
            cmd.append("--all")
        
        result = subprocess.run(cmd, capture_output=False)
        
        return provider, model, skill, result.returncode
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(items), 4)) as executor:
        futures = {executor.submit(run_single_eval, item): item for item in items}
        
        failed_count = 0
        for future in concurrent.futures.as_completed(futures):
            try:
                provider, model, skill, exit_code = future.result()
                display = f"{provider}/{model}" + (f"/{skill}" if skill else "")
                if exit_code == 0:
                    print(f"✅ [{display}] Completed")
                else:
                    print(f"❌ [{display}] Failed (exit code {exit_code})")
                    failed_count += 1
            except Exception as e:
                print(f"❌ Error: {e}")
                failed_count += 1
    
    print(f"\n✓ All evaluation(s) completed ({len(items)-failed_count}/{len(items)} passed)")
    
    if failed_count > 0:
        print(f"⚠ {failed_count} evaluation(s) failed")
    
    # Consolidate
    subprocess.run(["python3", "ci/consolidate_results.py"])


def parse_command(comment: str) -> tuple:
    """Parse /test command from comment."""
    filter_provider = "all"
    use_parallel = False

    if "/test copilot" in comment:
        filter_provider = "copilot"
    elif "/test ollama" in comment:
        filter_provider = "ollama"
    elif "/test gemini" in comment:
        filter_provider = "gemini"

    if "parallel" in comment:
        use_parallel = True

    return filter_provider, use_parallel


def main():
    parser = argparse.ArgumentParser(description="Orchestrate skill evaluations")
    parser.add_argument("pr_number", type=int, help="GitHub PR number")
    parser.add_argument("--filter-provider", default="all", help="Filter by provider")
    parser.add_argument("--parallel", action="store_true", help="Run in parallel (GitHub Actions mode)")
    parser.add_argument("--threshold", type=int, default=50, help="Pass threshold")
    parser.add_argument("--matrix-only", action="store_true", help="Only output matrix JSON and exit")

    args = parser.parse_args()

    # Validate environment
    if not args.matrix_only:
        validate_environment()

    # Export for child scripts
    os.environ["PR_NUMBER"] = str(args.pr_number)
    os.environ["COPILOT_GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN", "")
    os.environ["GH_TOKEN"] = os.environ.get("GITHUB_TOKEN", "")

    # Detect changes
    modified_skills = detect_changes(args.pr_number)
    os.environ["MODIFIED_SKILLS"] = modified_skills

    # Generate matrix (expand with per-skill jobs if skills detected)
    items = generate_matrix(args.filter_provider, modified_skills)
    
    # If matrix-only mode, output JSON and exit
    if args.matrix_only:
        print(json.dumps({"include": items}))
        sys.exit(0)

    # Clean previous results
    results_base = Path("tests/results")
    import shutil
    if results_base.exists():
        shutil.rmtree(results_base)
    results_base.mkdir(parents=True, exist_ok=True)

    # Run evaluations
    if args.parallel:
        run_parallel_local(items, args.threshold)
    else:
        run_sequential(items, args.threshold)


if __name__ == "__main__":
    main()

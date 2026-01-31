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
    print("\n==> Detecting changes")

    result = subprocess.run(
        ["python3", "ci/detect_changes.py", str(pr_number)],
        capture_output=True,
        text=True,
    )

    modified_skills = result.stdout.strip()

    if modified_skills:
        print(f"✓ Will test skills: {modified_skills}")
    else:
        print("✓ Will test all skills")

    return modified_skills


def generate_matrix(filter_provider: str = "all") -> list:
    """Generate evaluation matrix from configuration."""
    print("\n==> Generating evaluation matrix")

    result = subprocess.run(
        ["uv", "run", "--with", "pyyaml", "ci/matrix_generator.py", "--filter-provider", filter_provider],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("❌ Error generating matrix")
        sys.exit(1)

    try:
        matrix_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("❌ Error parsing matrix JSON")
        sys.exit(1)

    items = matrix_data.get("include", [])

    if not items:
        print("❌ Error: No enabled providers in configuration")
        sys.exit(1)

    print(f"✓ Generated matrix with {len(items)} configurations")
    for item in items:
        print(f"  - {item['display_name']}")

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


def run_parallel(items: list, threshold: int = 50):
    """Run evaluations in parallel (for GitHub Actions matrix strategy)."""
    print("\n==> Running evaluations in parallel")
    print("(This is for GitHub Actions matrix strategy - not running locally)")

    for item in items:
        print(f"  Will run: {item['display_name']}")

    print("\nUse GitHub Actions matrix strategy in workflow for true parallelization")


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

    args = parser.parse_args()

    # Validate environment
    validate_environment()

    # Export for child scripts
    os.environ["PR_NUMBER"] = str(args.pr_number)
    os.environ["COPILOT_GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN", "")
    os.environ["GH_TOKEN"] = os.environ.get("GITHUB_TOKEN", "")

    # Detect changes
    modified_skills = detect_changes(args.pr_number)
    os.environ["MODIFIED_SKILLS"] = modified_skills

    # Generate matrix
    items = generate_matrix(args.filter_provider)

    # Clean previous results
    results_base = Path("tests/results")
    import shutil
    if results_base.exists():
        shutil.rmtree(results_base)
    results_base.mkdir(parents=True, exist_ok=True)

    # Run evaluations
    if args.parallel:
        run_parallel(items, args.threshold)
    else:
        run_sequential(items, args.threshold)


if __name__ == "__main__":
    main()

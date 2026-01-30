#!/usr/bin/env python3
"""
Dynamic Benchmark Harness for Programming Skills

Discovers skills automatically from the filesystem and generates
test cases on-the-fly. No hardcoded skill names.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class Skill:
    name: str
    path: Path
    description: str
    content: str


def load_config(config_path: Path = Path("config.yaml")) -> dict:
    """Load configuration from YAML file."""
    if yaml is None:
        raise ImportError("pyyaml is required. Install with: uv pip install pyyaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def discover_skills(skills_dir: Path) -> list[Skill]:
    """Dynamically discover all skills from the skills directory."""
    skills = []

    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        return skills

    for item in skills_dir.iterdir():
        if item.is_dir():
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text(encoding='utf-8')
                # Extract description from YAML frontmatter or first paragraph
                description = ""
                if content.startswith("---"):
                    # Extract from frontmatter
                    if match := re.search(r'description:\s*["\']?(.+?)["\']?\s*\n', content):
                        description = match.group(1)
                else:
                    # Extract from first paragraph
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip() and not line.startswith('#'):
                            description = line.strip()
                            break

                skills.append(Skill(
                    name=item.name,
                    path=item,
                    description=description,
                    content=content
                ))

    return sorted(skills, key=lambda s: s.name)


def generate_test_cases(skill: Skill) -> list[dict]:
    """Generate test cases from skill content dynamically."""
    tests = []
    content = skill.content

    # Extract examples (both good and bad)
    # Use Unicode escape sequences for emoji characters
    good_pattern = r'###\s*[' + r'\u2705' + r'][^`]*```[^\n]*\n([^`]+)```'
    bad_pattern = r'###\s*[' + r'\u274c' + r'][^`]*```[^\n]*\n([^`]+)```'

    good_examples = re.findall(good_pattern, content, re.DOTALL)
    bad_examples = re.findall(bad_pattern, content, re.DOTALL)

    # Generate test for recognizing good patterns
    for i, example in enumerate(good_examples[:2]):  # Limit to first 2
        tests.append({
            "name": f"recognize_good_{i+1}",
            "input": f"Review this code from the perspective of '{skill.name}':\n\n{example[:500]}",
            "expected": {
                "does_not_contain": ["should", "wrong", "fix", "avoid", "\u274c"],
                "contains_any": ["good", "correct", "\u2705", "follows", "proper"]
            }
        })

    # Generate test for identifying bad patterns
    for i, example in enumerate(bad_examples[:2]):  # Limit to first 2
        tests.append({
            "name": f"identify_bad_{i+1}",
            "input": f"Review this code from the perspective of '{skill.name}':\n\n{example[:500]}",
            "expected": {
                "contains_any": ["should", "avoid", "\u274c", "wrong", "fix", "separate", "violation"]
            }
        })

    # Generate test for explaining the principle
    tests.append({
        "name": "explain_principle",
        "input": f"Explain the principle of '{skill.name}' and when to apply it.",
        "expected": {
            "contains_any": skill.description.lower().split()[:5] if skill.description else ["principle"],
            "min_length": 50
        }
    })

    return tests


def save_test_cases(skill: Skill, tests: list[dict], output_dir: Path) -> Path:
    """Save generated test cases to JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    test_file = output_dir / f"{skill.name}.json"

    data = {
        "skill": skill.name,
        "generated_from": str(skill.path),
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
        "tests": tests
    }

    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    return test_file


def check_ollama_running(base_url: str) -> bool:
    """Check if Ollama server is running."""
    try:
        import urllib.request
        host = base_url.replace('/v1', '')
        urllib.request.urlopen(f"{host}/api/tags", timeout=5)
        return True
    except Exception:
        return False


def run_upskill_eval(
    skill: Skill,
    model: str,
    test_file: Path,
    base_url: Optional[str],
    verbose: bool = False
) -> dict:
    """Run upskill eval on a skill."""
    cmd = [
        sys.executable, "-m", "upskill", "eval", str(skill.path),
        "-m", model,
        "-t", str(test_file),
        "--runs-dir", "./results/runs",
        "--no-baseline"
    ]

    if base_url:
        cmd.extend(["--base-url", base_url, "--provider", "generic"])

    if verbose:
        cmd.append("-v")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        # Parse pass rate from output
        output = result.stdout + result.stderr
        pass_rate = None
        if match := re.search(r'(\d+)%', output):
            pass_rate = int(match.group(1))

        return {
            "skill": skill.name,
            "model": model,
            "success": result.returncode == 0,
            "pass_rate": pass_rate,
            "output": output[-2000:] if len(output) > 2000 else output,  # Truncate
            "returncode": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {"skill": skill.name, "model": model, "success": False, "error": "Timeout"}
    except Exception as e:
        return {"skill": skill.name, "model": model, "success": False, "error": str(e)}


def generate_dynamic_report(results_dir: Path) -> str:
    """Generate report from results."""
    if not results_dir.exists():
        return "No results found."

    lines = ["# Benchmark Results", ""]
    lines.append("| Skill | Model | Pass Rate | Status |")
    lines.append("|-------|-------|-----------|--------|")

    # Find all result files
    for result_file in sorted(results_dir.glob("**/*.json")):
        try:
            with open(result_file, encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for r in data:
                        if isinstance(r, dict) and 'skill' in r:
                            status = "OK" if r.get('success') else "FAIL"
                            pass_rate = r.get('pass_rate', 'N/A')
                            lines.append(f"| {r.get('skill', '?')} | {r.get('model', '?')} | {pass_rate} | {status} |")
        except Exception:
            continue

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Dynamic benchmark harness")
    parser.add_argument("--skill", help="Specific skill to test (name or path)")
    parser.add_argument("--all", action="store_true", help="Test all discovered skills")
    parser.add_argument("--model", action="append", help="Model(s) to test")
    parser.add_argument("--config", default="config.yaml", help="Config file")
    parser.add_argument("--check", action="store_true", help="Check prerequisites")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Load config
    config = load_config(Path(args.config))
    skills_dir = Path(config.get('skills_dir', '../skills')).resolve()
    results_dir = Path(config.get('runs_dir', './results/runs'))

    if args.check:
        print("Checking prerequisites...")
        try:
            subprocess.run([sys.executable, "-m", "upskill", "--version"],
                         capture_output=True, check=True)
            print("[OK] upskill installed")
        except Exception:
            print("[FAIL] upskill not found. Run: uv pip install upskill")
            return 1

        ollama_url = config.get('ollama', {}).get('base_url', 'http://localhost:11434/v1')
        if check_ollama_running(ollama_url):
            print(f"[OK] Ollama running at {ollama_url}")
        else:
            print(f"[WARN] Ollama not running at {ollama_url} (start with: ollama serve)")

        skills = discover_skills(skills_dir)
        print(f"[OK] Found {len(skills)} skills in {skills_dir}")
        return 0

    if args.report:
        print(generate_dynamic_report(results_dir))
        return 0

    # Discover skills
    all_skills = discover_skills(skills_dir)
    if not all_skills:
        print(f"No skills found in {skills_dir}")
        return 1

    # Filter skills to test
    if args.skill:
        skills_to_test = [s for s in all_skills if args.skill in s.name]
        if not skills_to_test:
            print(f"Skill '{args.skill}' not found. Available: {', '.join(s.name for s in all_skills)}")
            return 1
    else:
        skills_to_test = all_skills

    # Get models
    models = args.model or [config.get('model', 'llama3.2:latest')]

    # Check Ollama
    ollama_url = config.get('ollama', {}).get('base_url', 'http://localhost:11434/v1')
    if 'localhost' in ollama_url or '127.0.0.1' in ollama_url:
        if not check_ollama_running(ollama_url):
            print(f"Error: Ollama not running at {ollama_url}")
            return 1

    # Run benchmarks
    results_dir.mkdir(parents=True, exist_ok=True)
    test_cases_dir = Path("test_cases")
    test_cases_dir.mkdir(exist_ok=True)

    all_results = []

    for model in models:
        print(f"\n{'=' * 60}")
        print(f"Model: {model}")
        print(f"{'=' * 60}")

        for skill in skills_to_test:
            print(f"\nTesting: {skill.name}")
            print("-" * 40)

            # Generate test cases dynamically
            tests = generate_test_cases(skill)
            test_file = save_test_cases(skill, tests, test_cases_dir)
            print(f"  Generated {len(tests)} test cases")

            # Run evaluation
            result = run_upskill_eval(skill, model, test_file, ollama_url, args.verbose)
            all_results.append(result)

            status = "OK" if result.get('success') else "FAIL"
            pass_rate = result.get('pass_rate', 'N/A')
            print(f"  [{status}] Pass rate: {pass_rate}%")

            if result.get('error'):
                print(f"  Error: {result['error']}")

    # Save summary
    summary = {
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
        "skills_tested": [s.name for s in skills_to_test],
        "models": models,
        "results": all_results
    }

    summary_file = results_dir / "summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Complete. Summary: {summary_file}")
    print(f"Run 'uv run python harness.py --report' to view results")

    return 0


if __name__ == "__main__":
    sys.exit(main())

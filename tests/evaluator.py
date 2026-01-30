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
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Any
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
    severity: str = "SUGGEST"  # Default severity


def load_config(config_path: Path = Path("tests/config.yaml")) -> dict:
    """Load configuration from YAML file. Checks root and tests/ directory."""
    if yaml is None:
        raise ImportError("pyyaml is required. Install with: uv pip install pyyaml")
    
    # Try specified path, then root
    paths = [config_path, Path("config.yaml")]
    for path in paths:
        if path.exists():
            with open(path, 'r') as f:
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
                # Extract description and severity from YAML frontmatter
                description = ""
                severity = "SUGGEST"
                
                if content.startswith("---"):
                    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                    if frontmatter_match:
                        frontmatter = frontmatter_match.group(1)
                        if desc_match := re.search(r'description:\s*["\']?(.+?)["\']?\s*\n', frontmatter):
                            description = desc_match.group(1)
                        if sev_match := re.search(r'severity:\s*(\w+)', frontmatter):
                            severity = sev_match.group(1).upper()
                
                if not description:
                    # Extract from first paragraph
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip() and not line.startswith('#') and not line.startswith('---'):
                            description = line.strip()
                            break

                skills.append(Skill(
                    name=item.name,
                    path=item,
                    description=description,
                    content=content,
                    severity=severity
                ))

    return sorted(skills, key=lambda s: s.name)


def generate_test_cases(skill: Skill, verbose: bool = False) -> list[dict]:
    """Generate test cases from skill directory. Prioritizes test.json over markdown scenarios."""
    tests = []
    
    # 1. Look for standalone test.json (v2.2.0 preferred) or tests.json (v2.1.0 legacy)
    for filename in ["test.json", "tests.json"]:
        json_path = skill.path / filename
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    raw_tests = []
                    if isinstance(data, list):
                        raw_tests = data
                    elif isinstance(data, dict):
                        raw_tests = data.get('tests', [])
                    
                    # Process inputs: check for external files
                    for test in raw_tests:
                        input_val = test.get('input', '')
                        if isinstance(input_val, str) and input_val.strip() and not '\n' in input_val:
                            # Potential filename: check if it exists in skill directory
                            external_file = skill.path / input_val.strip()
                            if external_file.exists() and external_file.is_file():
                                if verbose:
                                    print(f"    [INFO] Loading external input from {input_val}")
                                # Replace the filename with its content, but keep a label without the path
                                file_content = external_file.read_text(encoding='utf-8')
                                test['input'] = f"CODE CONTENT ({input_val}):\n\n{file_content}"
                    
                    return raw_tests
            except Exception as e:
                print(f"  [WARN] Failed to parse {json_path}: {e}")

    # 2. Fallback to specialized Benchmark Scenarios section in SKILL.md
    content = skill.content
    scenario_section = re.search(r'## Benchmark Scenarios\s*\n(.*?)(?=\n##|$)', content, re.DOTALL)
    if scenario_section:
        scenario_content = scenario_section.group(1)
        # Look for JSON blocks in the scenario section
        json_blocks = re.findall(r'```json\n(.*?)\n```', scenario_content, re.DOTALL)
        for block in json_blocks:
            try:
                data = json.loads(block)
                if isinstance(data, list):
                    tests.extend(data)
                elif isinstance(data, dict):
                    tests.append(data)
            except Exception:
                continue

    return tests


def save_test_cases(skill: Skill, tests: list[dict], output_dir: Path) -> Path:
    """Save generated test cases to JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    test_file = output_dir / f"{skill.name}.json"

    data = {
        "skill": skill.name,
        "severity": skill.severity,
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
        host = base_url.replace('/v1', '')
        urllib.request.urlopen(f"{host}/api/tags", timeout=5)
        return True
    except Exception:
        return False


def call_ollama(prompt: str, model: str, base_url: str, options: dict = None) -> str:
    """Call Ollama chat API directly."""
    url = f"{base_url}/chat/completions"
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "options": options or {}
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=300) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res['choices'][0]['message']['content']
    except Exception as e:
        return f"Error calling Ollama: {str(e)}"


def call_copilot_cli(prompt: str, model: str, verbose: bool = False) -> str:
    """Call GitHub Copilot CLI."""
    if verbose:
        print(f"      [DEBUG] Calling Copilot CLI with model: {model}")
    
    try:
        # Use subprocess with list for safer argument handling
        # --yolo skips confirmations, --silent outputs just the result
        # --deny-tool 'write' prevents the agent from modifying local files
        cmd = ["copilot", "-p", prompt, "--model", model, "--silent", "--yolo", "--deny-tool", "write"]
        
        # We use a large timeout as cloud models can sometimes be slow
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            timeout=300
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() or "Unknown error"
            return f"Error calling Copilot CLI: {error_msg}"
            
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error calling Copilot CLI: Request timed out"
    except Exception as e:
        return f"Error calling Copilot CLI: {str(e)}"


def evaluate_response(response: str, expected: dict) -> tuple[bool, str]:
    """Evaluate a response against expectations. Returns (pass, reason)."""
    response_lower = response.lower()

    # 1. Excludes (None of these must match)
    excludes = expected.get('excludes', []) + expected.get('does_not_contain', [])
    for term in excludes:
        if term.lower() in response_lower:
            return False, f"Found excluded term: {term}"

    # 2. Includes (ALL of these must match)
    includes = expected.get('includes', [])
    for term in includes:
        if term.lower() not in response_lower:
            return False, f"Missing included term: {term}"

    # 3. Contains Any (Legacy: AT LEAST ONE must match)
    contains_any = expected.get('contains_any', [])
    if contains_any:
        found = False
        for term in contains_any:
            if term.lower() in response_lower:
                found = True
                break
        if not found:
            return False, f"Missing all terms from contains_any: {contains_any}"

    # 4. Regex (ALL of these must match)
    regexes = expected.get('regex', [])
    if isinstance(regexes, str):
        regexes = [regexes]
    for pattern in regexes:
        if not re.search(pattern, response, re.IGNORECASE | re.DOTALL):
            return False, f"Regex failed to match: {pattern}"

    # 5. Length Constraints
    if 'min_length' in expected and len(response) < expected['min_length']:
        return False, f"Response too short: {len(response)} < {expected['min_length']}"
    
    if 'max_length' in expected and len(response) > expected['max_length']:
        return False, f"Response too long: {len(response)} > {expected['max_length']}"

    return True, ""


def run_benchmark_eval(
    skill: Skill,
    model: str,
    test_file: Path,
    base_url: str,
    provider: str = "ollama",
    num_ctx: int = 64000,
    verbose: bool = False
) -> dict:
    """Run benchmark evaluation on a skill with Baseline vs Skill comparison."""
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
            tests = test_data.get('tests', [])
    except Exception as e:
        return {"skill": skill.name, "success": False, "error": f"Failed to load tests: {e}"}

    results = []
    passed_baseline = 0
    passed_skill = 0

    skill_instruction = f"Apply the following programming skill to your response:\n\n{skill.content}\n\n"

    for test in tests:
        if verbose:
            print(f"    Running test: {test['name']}...")

        # 1. Baseline Run (No skill context)
        prompt_baseline = test['input']
        if provider == "copilot":
            response_baseline = call_copilot_cli(prompt_baseline, model, verbose)
        else:
            response_baseline = call_ollama(prompt_baseline, model, base_url, options={"num_ctx": num_ctx})
            
        pass_baseline, reason_baseline = evaluate_response(response_baseline, test['expected'])
        if pass_baseline:
            passed_baseline += 1
        elif verbose:
            print(f"      [BASELINE FAIL] {test['name']}: {reason_baseline}")

        # 2. Skill Run (Skill context prepended)
        prompt_skill = skill_instruction + test['input']
        if provider == "copilot":
            response_skill = call_copilot_cli(prompt_skill, model, verbose)
        else:
            response_skill = call_ollama(prompt_skill, model, base_url, options={"num_ctx": num_ctx})
            
        pass_skill, reason_skill = evaluate_response(response_skill, test['expected'])
        if pass_skill:
            passed_skill += 1
        elif verbose:
            print(f"      [SKILL FAIL] {test['name']}: {reason_skill}")
            if verbose:
                print(f"      Response: {response_skill[:200]}...")

        results.append({
            "name": test['name'],
            "baseline": {
                "pass": pass_baseline, 
                "response_preview": response_baseline[:100] + "...",
                "response_full": response_baseline
            },
            "skill": {
                "pass": pass_skill, 
                "response_preview": response_skill[:100] + "...",
                "response_full": response_skill
            }
        })

    baseline_rate = int((passed_baseline / len(tests)) * 100) if tests else 0
    skill_rate = int((passed_skill / len(tests)) * 100) if tests else 0
    improvement = skill_rate - baseline_rate

    return {
        "skill": skill.name,
        "severity": skill.severity,
        "model": model,
        "success": True,
        "baseline_rate": baseline_rate,
        "skill_rate": skill_rate,
        "improvement": improvement,
        "results": results,
        "output": f"Baseline: {baseline_rate}% | With Skill: {skill_rate}% | Improvement: {improvement:+}%"
    }
def generate_dynamic_report(results_dir: Path) -> str:
    """Generate report from summary.json."""
    summary_file = results_dir / "summary.json"
    if not summary_file.exists():
        return "No summary file found. Run a benchmark first."

    lines = ["# Benchmark Results", ""]
    lines.append("| Skill | Severity | Model | Baseline | With Skill | Improvement | Status |")
    lines.append("|-------|----------|-------|----------|------------|-------------|--------|")

    try:
        with open(summary_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            results = data.get('results', [])
            for r in results:
                baseline = r.get('baseline_rate', 0)
                skill = r.get('skill_rate', 0)
                improvement = r.get('improvement', 0)
                severity = r.get('severity', 'SUGGEST')
                status = "+" if improvement > 0 else ("-" if improvement < 0 else "~")
                imp_str = f"{improvement:+}%"
                lines.append(f"| {r['skill']} | {severity} | {r['model']} | {baseline}% | {skill}% | {imp_str} | {status} |")
    except Exception as e:
        return f"Error generating report: {e}"

    return "\n".join(lines)


def generate_github_comment(results_dir: Path) -> str:
    """Generate a detailed Markdown comment for GitHub PRs."""
    summary_file = results_dir / "summary.json"
    if not summary_file.exists():
        return "No results found."

    try:
        with open(summary_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            results = data.get('results', [])
            
            lines = ["## [SKILL EVALUATION] Results", ""]
            lines.append("| Skill | Status | Baseline | With Skill | Improvement |")
            lines.append("|-------|--------|----------|------------|-------------|")
            
            for r in results:
                baseline = r.get('baseline_rate', 0)
                skill = r.get('skill_rate', 0)
                improvement = r.get('improvement', 0)
                status = "+" if improvement > 0 else ("-" if improvement < 0 else "~")
                lines.append(f"| {r['skill']} | {status} | {baseline}% | {skill}% | {improvement:+}% |")
            
            lines.append("\n---")
            lines.append("\n### [DEBUG] Detailed Info")
            
            for r in results:
                lines.append(f"\n<details>")
                lines.append(f"<summary><b>{r['skill']}</b> ({r.get('skill_rate', 0)}% pass rate)</summary>\n")
                
                for test in r.get('results', []):
                    test_status = "[PASS]" if test['skill']['pass'] else "[FAIL]"
                    lines.append(f"\n#### {test_status} {test['name']}")
                    lines.append("\n**AI Generated Code:**")
                    lines.append(f"\n```javascript")
                    lines.append(test['skill']['response_full'])
                    lines.append("```")
                
                lines.append("\n</details>")
                
            return "\n".join(lines)
    except Exception as e:
        return f"Error generating GitHub comment: {e}"


# Deleted duplicated load_config


def main():
    parser = argparse.ArgumentParser(description="Skill Benchmark Harness")
    parser.add_argument("--skill", action="append", help="Test specific skill(s)")
    parser.add_argument("--all", action="store_true", help="Test all skills")
    parser.add_argument("--model", action="append", help="Model(s) to use")
    parser.add_argument("--provider", choices=["ollama", "copilot"], default="ollama", help="Model provider (default: ollama)")
    parser.add_argument("--threshold", type=int, default=50, help="Minimum pass rate threshold (default: 50)")
    parser.add_argument("--report", action="store_true", help="Generate console report")
    parser.add_argument("--github-comment", action="store_true", help="Generate comment.md for PRs")
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    parser.add_argument("--check-only", action="store_true", help="Quick check of setup")
    args = parser.parse_args()

    config = load_config()
    skills_dir = Path(config.get('skills_dir', 'skills'))
    results_dir = Path(config.get('runs_dir', 'results/runs'))

    if args.check_only:
        print("Checking prerequisites...")
        # Check if upskill is available
        try:
            import upskill  # type: ignore
            try:
                # Try to get version if available
                import importlib.metadata
                version = importlib.metadata.version("upskill")
                print(f"[OK] upskill installed ({version})")
            except Exception:
                print("[OK] upskill installed")
        except ImportError:
            print("[FAIL] upskill not found. Run: uv pip install upskill")
            return 1

        ollama_url = config.get('ollama', {}).get('base_url', 'http://localhost:11434/v1')
        if check_ollama_running(ollama_url):
            print(f"[OK] Ollama running at {ollama_url}")
        else:
            print(f"[WARN] Ollama not running at {ollama_url} (start with: ollama serve)")

    # Discover skills early for report generation or filtering
    all_skills = discover_skills(skills_dir)
    if not all_skills:
        print(f"No skills found in {skills_dir}")
        # Only return 1 if we're not just generating a report
        if not args.report:
            return 1

    # If only --report or --github-comment is provided, generate and exit
    if (args.report or args.github_comment) and not (args.all or args.skill):
        if args.report:
            print(generate_dynamic_report(results_dir))
        if args.github_comment:
            comment_content = generate_github_comment(results_dir)
            if comment_content:
                with open("comment.md", "w", encoding="utf-8") as f:
                    f.write(comment_content)
                print("\n[OK] PR comment generated in comment.md")
        return 0

    # Filter skills to test
    if args.skill:
        skills_to_test = []
        for s_name in args.skill:
            matches = [s for s in all_skills if s_name in s.name]
            skills_to_test.extend(matches)
        
        # Deduplicate
        skills_to_test = list({s.name: s for s in skills_to_test}.values())
        
        if not skills_to_test:
            print(f"None of the requested skills found: {', '.join(args.skill)}. Available: {', '.join(s.name for s in all_skills)}")
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
    test_cases_dir = Path("tests/test_cases")
    test_cases_dir.mkdir(exist_ok=True)

    all_results = []
    num_ctx = config.get('ollama', {}).get('num_ctx', 64000)

    for model in models:
        print(f"\n{'=' * 60}")
        print(f"Model: {model} (Context: {num_ctx})")
        print(f"{'=' * 60}")

        for skill in skills_to_test:
            print(f"\nTesting: {skill.name}")
            print("-" * 40)

            # Generate test cases dynamically
            tests = generate_test_cases(skill, args.verbose)
            test_file = save_test_cases(skill, tests, test_cases_dir)
            print(f"  Generated {len(tests)} test cases")

            # Run evaluation
            result = run_benchmark_eval(
                skill, 
                model, 
                test_file, 
                ollama_url, 
                provider=args.provider,
                num_ctx=num_ctx, 
                verbose=args.verbose
            )
            all_results.append(result)

            status = "OK" if result.get('success') else "FAIL"
            pass_rate = result.get('skill_rate', 'N/A')
            print(f"  [{status}] Pass rate (Skill): {pass_rate}%")

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

    if args.report:
        print(f"\n{generate_dynamic_report(results_dir)}")

    if args.github_comment:
        comment_content = generate_github_comment(results_dir)
        with open("comment.md", "w", encoding="utf-8") as f:
            f.write(comment_content)
        print("\n[OK] PR comment generated in comment.md")

    # Check for threshold failures
    failed_skills = [
        r['skill'] for r in all_results 
        if r.get('success') and r.get('skill_rate', 0) < args.threshold
    ]
    
    if failed_skills:
        print(f"\n[FAIL] {len(failed_skills)} skills failed to meet the {args.threshold}% threshold: {', '.join(failed_skills)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

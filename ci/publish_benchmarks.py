#!/usr/bin/env python3
"""
Publish Benchmarks - Orchestration Script

Main entry point for publishing benchmark results.
Coordinates all steps: run evaluation, generate data, create HTML, push to orphan branch.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def run_benchmark(provider: str, model: str, skill: str | None = None) -> bool:
    """
    Run benchmark evaluation.

    Args:
        provider: Provider name (ollama, copilot, gemini)
        model: Model name
        skill: Optional specific skill to test

    Returns:
        True if successful, False otherwise
    """
    cmd = [
        "uv", "run", "--project", "tests", "tests/evaluator.py",
        "--provider", provider,
        "--model", model,
        "--judge",
        "--verbose",
        "--report",
    ]

    if skill:
        cmd.extend(["--skill", skill])

    print(f"Running benchmark: provider={provider}, model={model}")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)

    return result.returncode == 0


def _timestamp_for_id(timestamp: str | None) -> str:
    """
    Convert ISO timestamp to YYYYMMDD-HHMMSS format for benchmark_id.
    """
    if timestamp:
        normalized = timestamp.rstrip("Z")
        try:
            dt = datetime.fromisoformat(normalized)
            return dt.strftime("%Y%m%d-%H%M%S")
        except ValueError:
            pass
    return time.strftime("%Y%m%d-%H%M%S")


def _load_summary_timestamp(summary_path: Path) -> str | None:
    if not summary_path.exists():
        return None
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        return data.get("timestamp")
    except Exception:
        return None


def _safe_model_for_id(model: str) -> str:
    return model.replace("/", "-")


def collect_and_generate(benchmarks_dir: Path, output_dir: Path, script_src: Path) -> bool:
    """
    Collect benchmark data and generate HTML.

    Args:
        benchmarks_dir: Directory containing benchmark JSON files
        output_dir: Directory to write generated files

    Returns:
        True if successful, False otherwise
    """
    from generate_dashboard_data import generate_dashboard_data
    from generate_basic_html import generate_basic_html

    # Generate aggregated JSON and per-run data.json files
    data_file = output_dir / "benchmarks.json"
    if not generate_dashboard_data(benchmarks_dir, data_file):
        print("Error generating dashboard data")
        return False

    # Copy app.js to output scripts directory
    scripts_dir = output_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    if script_src.exists():
        shutil.copy2(script_src, scripts_dir / "app.js")
    else:
        print(f"Warning: app.js not found at {script_src}")

    # Generate aggregate HTML
    html_file = output_dir / "index.html"
    if not generate_basic_html(data_file, html_file, data_src="benchmarks.json", script_src="scripts/app.js"):
        print("Error generating HTML")
        return False

    # Generate per-run HTML pages
    for run_data_file in output_dir.glob("*/data.json"):
        run_html = run_data_file.parent / "index.html"
        if not generate_basic_html(run_data_file, run_html, data_src="data.json", script_src="../scripts/app.js"):
            print(f"Error generating HTML for {run_data_file.parent}")
            return False

    return True


def push_to_orphan_branch(repo_path: Path, docs_dir: Path, branch_name: str) -> bool:
    """
    Push benchmark files to orphan branch.

    Args:
        repo_path: Path to git repository
        docs_dir: Path to docs directory
        branch_name: Name of orphan branch

    Returns:
        True if successful, False otherwise
    """
    from orphan_branch_manager import manage_benchmark_branch

    return manage_benchmark_branch(repo_path, docs_dir, branch_name)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Publish benchmark results")
    parser.add_argument("--provider", required=True, help="Provider name")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--skill", help="Optional specific skill to test")
    parser.add_argument("--branch", default="benchmark-history", help="Orphan branch name")
    parser.add_argument("--no-benchmark", action="store_true", help="Skip benchmark run")
    parser.add_argument("--no-push", action="store_true", help="Skip pushing to orphan branch")
    parser.add_argument("--benchmarks-dir", help="Directory containing benchmark JSON files (defaults to output dir)")
    parser.add_argument("--results-dir", help="Directory containing summary.json (default: tests/results)")
    parser.add_argument("--output-dir", help="Directory to write generated files")

    args = parser.parse_args()

    repo_path = Path(__file__).parent.parent
    results_dir = Path(args.results_dir) if args.results_dir else repo_path / "tests" / "results"
    docs_dir = Path(args.output_dir) if args.output_dir else repo_path / "docs" / "benchmarks"
    benchmarks_dir = Path(args.benchmarks_dir) if args.benchmarks_dir else docs_dir

    if benchmarks_dir != docs_dir:
        print("Error: --benchmarks-dir must match --output-dir for this workflow")
        return 1

    # Ensure docs directory exists (may not exist if no docs yet)
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Run benchmark if requested
    if not args.no_benchmark:
        if not run_benchmark(args.provider, args.model, args.skill):
            print("Benchmark run failed")
            return 1
    else:
        print("Skipping benchmark run")

    # Step 2: Copy summary.json into versioned run folder
    summary_path = results_dir / "summary.json"
    if not summary_path.exists():
        print(f"Summary not found at {summary_path}")
        return 1

    timestamp = _load_summary_timestamp(summary_path)
    timestamp_id = _timestamp_for_id(timestamp)
    benchmark_id = f"{args.provider}-{_safe_model_for_id(args.model)}-{timestamp_id}"
    run_dir = docs_dir / benchmark_id
    run_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(summary_path, run_dir / "summary.json")

    # Step 3: Generate dashboard data and HTML
    print("\nGenerating dashboard data...")
    script_src = Path(__file__).parent / "scripts" / "app.js"
    if not collect_and_generate(benchmarks_dir, docs_dir, script_src):
        print("Dashboard generation failed")
        return 1

    # Step 4: Push to orphan branch if requested
    if not args.no_push:
        print("\nPushing to orphan branch...")
        if not push_to_orphan_branch(repo_path, docs_dir, args.branch):
            print("Push to orphan branch failed")
            return 1
    else:
        print("Skipping push to orphan branch")

    print("\n✓ Benchmark publishing completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

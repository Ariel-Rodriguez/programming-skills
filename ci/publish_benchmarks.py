#!/usr/bin/env python3
"""
Publish Benchmarks - Orchestration Script

Main entry point for publishing benchmark results.
Coordinates all steps: run evaluation, generate data, create HTML, push to orphan branch.
"""

import argparse
import subprocess
import sys
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


def collect_and_generate(benchmarks_dir: Path, output_dir: Path) -> bool:
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

    # Generate aggregated JSON
    data_file = output_dir / "benchmarks.json"
    if not generate_dashboard_data(benchmarks_dir, data_file):
        print("Error generating dashboard data")
        return False

    # Generate HTML
    html_file = output_dir / "index.html"
    if not generate_basic_html(data_file, html_file):
        print("Error generating HTML")
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

    args = parser.parse_args()

    repo_path = Path(__file__).parent.parent
    benchmarks_dir = repo_path / "tests" / "results"
    docs_dir = repo_path / "docs"

    # Step 1: Run benchmark if requested
    if not args.no_benchmark:
        if not run_benchmark(args.provider, args.model, args.skill):
            print("Benchmark run failed")
            return 1
    else:
        print("Skipping benchmark run")

    # Step 2: Generate dashboard data and HTML
    print("\nGenerating dashboard data...")
    if not collect_and_generate(benchmarks_dir, docs_dir):
        print("Dashboard generation failed")
        return 1

    # Step 3: Push to orphan branch if requested
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

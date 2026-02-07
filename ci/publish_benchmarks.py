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


def _find_latest_summary(results_dir: Path) -> Path | None:
    candidates = (
        list(results_dir.glob("summary-*.json"))
        + list(results_dir.glob("summary.json"))
        + list(results_dir.glob("*.json"))
    )
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _write_history_from_summary(summary_path: Path, history_dir: Path, provider: str | None = None) -> bool:
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error reading summary {summary_path}: {e}")
        return False

    timestamp = data.get("timestamp", "")
    stamp = _timestamp_for_id(timestamp)
    results = data.get("results", [])

    for result in results:
        skill = result.get("skill", "unknown")
        model = result.get("model", "unknown")
        out_dir = history_dir / skill
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f\"{model}-{stamp}.json\"

        payload = {
            \"timestamp\": timestamp,
            \"skill\": skill,
            \"severity\": result.get(\"severity\"),
            \"model\": model,
            \"baseline_rate\": result.get(\"baseline_rate\"),
            \"skill_rate\": result.get(\"skill_rate\"),
            \"baseline_rating\": result.get(\"baseline_rating\"),
            \"skill_rating\": result.get(\"skill_rating\"),
            \"baseline_pass_count\": result.get(\"baseline_pass_count\"),
            \"skill_pass_count\": result.get(\"skill_pass_count\"),
            \"improvement\": result.get(\"improvement\"),
            \"results\": result.get(\"results\", []),
        }
        if result.get(\"judgment\") is not None:
            payload[\"judgment\"] = result.get(\"judgment\")
        if provider:
            payload[\"provider\"] = provider

        out_file.write_text(json.dumps(payload, indent=2))

    return True


def collect_and_generate(history_dir: Path, output_dir: Path) -> bool:
    """
    Collect benchmark data and generate HTML.

    Args:
        benchmarks_dir: Directory containing benchmark JSON files
        output_dir: Directory to write generated files

    Returns:
        True if successful, False otherwise
    """
    from generate_dashboard_data import generate_dashboard_data
    # Generate aggregated JSON and per-run data.json files
    if not generate_dashboard_data(history_dir, output_dir):
        print("Error generating dashboard data")
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
    parser.add_argument("--provider", help="Provider name")
    parser.add_argument("--model", help="Model name")
    parser.add_argument("--skill", help="Optional specific skill to test")
    parser.add_argument("--branch", default="benchmark-history", help="Orphan branch name")
    parser.add_argument("--no-benchmark", action="store_true", help="Skip benchmark run")
    parser.add_argument("--no-push", action="store_true", help="Skip pushing to orphan branch")
    parser.add_argument("--benchmarks-dir", help="Deprecated (unused)")
    parser.add_argument("--results-dir", help="Directory containing summary.json (default: tests/results)")
    parser.add_argument("--history-dir", help="Directory containing per-skill history (default: tests/data-history)")
    parser.add_argument("--output-dir", help="Directory to write generated files")
    parser.add_argument("--summary-path", help="Path to summary json (overrides results-dir)")

    args = parser.parse_args()

    repo_path = Path(__file__).parent.parent
    if args.benchmarks_dir:
        print("Warning: --benchmarks-dir is deprecated and ignored.")

    results_dir = Path(args.results_dir) if args.results_dir else repo_path / "tests" / "results"
    history_dir = Path(args.history_dir) if args.history_dir else repo_path / "tests" / "data-history"
    output_dir = Path(args.output_dir) if args.output_dir else repo_path / "site" / "benchmarks"

    # Ensure docs directory exists (may not exist if no docs yet)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Run benchmark if requested
    if not args.no_benchmark:
        if not args.provider or not args.model:
            print("Error: --provider and --model are required unless --no-benchmark is set")
            return 1
        if not run_benchmark(args.provider, args.model, args.skill):
            print("Benchmark run failed")
            return 1
    else:
        print("Skipping benchmark run")

    # Step 2: Resolve summary input (optional import into history)
    if args.summary_path:
        summary_path = Path(args.summary_path)
    else:
        summary_path = results_dir / "summary.json"
        if not summary_path.exists():
            latest = _find_latest_summary(results_dir)
            if latest:
                summary_path = latest

    if summary_path.exists():
        history_dir.mkdir(parents=True, exist_ok=True)
        provider = args.provider if args.provider else None
        if not _write_history_from_summary(summary_path, history_dir, provider):
            print("Failed to import summary into history")
            return 1
    else:
        print(f"Summary not found at {summary_path} (skipping import)")

    # Step 4: Sync static site assets into output directory
    source_dir = repo_path / "src" / "pages" / "benchmarks"
    if not source_dir.exists():
        print(f"Static site source not found at {source_dir}")
        return 1

    for item in source_dir.iterdir():
        dest = output_dir / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # Step 5: Generate dashboard data files
    print("\nGenerating dashboard data...")
    if not collect_and_generate(history_dir, output_dir):
        print("Dashboard generation failed")
        return 1

    # Step 6: Push to orphan branch if requested
    if not args.no_push:
        print("\nPushing to orphan branch...")
        if not push_to_orphan_branch(repo_path, output_dir, args.branch):
            print("Push to orphan branch failed")
            return 1
    else:
        print("Skipping push to orphan branch")

    print("\n✓ Benchmark publishing completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

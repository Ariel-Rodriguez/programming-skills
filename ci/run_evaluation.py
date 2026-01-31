#!/usr/bin/env python3
"""
Execute evaluation for a single provider/model combination.

Policy-Mechanism Separation: Configuration passed as parameters.
Single Responsibility: Only runs evaluation, doesn't detect or orchestrate.
"""

import subprocess
import sys
import os
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print("Usage: run_evaluation.py <provider> <model> [threshold] [extra_args]")
        sys.exit(1)

    provider = sys.argv[1]
    model = sys.argv[2]
    threshold = sys.argv[3] if len(sys.argv) > 3 else "50"
    extra_args = sys.argv[4] if len(sys.argv) > 4 else ""

    # Results directory per provider/model for parallel execution
    results_dir = Path("tests/results") / provider / model.replace(":", "_").replace("/", "_")
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"==> Running evaluation: {provider}/{model}")
    print(f"    Results: {results_dir}")
    print(f"    Threshold: {threshold}")

    # Build skill arguments
    skill_args = []
    modified_skills = os.environ.get("MODIFIED_SKILLS", "").strip()
    if modified_skills:
        for skill in modified_skills.split():
            skill_args.extend(["--skill", skill])
    else:
        skill_args = ["--all"]

    # Build command
    cmd = [
        "uv",
        "run",
        "--project",
        "tests",
        "tests/evaluator.py",
        "--provider",
        provider,
        "--model",
        model,
        "--threshold",
        threshold,
        "--results-dir",
        str(results_dir),
        "--report",
        "--judge",
        "--verbose",
    ]

    # Add extra args if provided
    if extra_args.strip():
        cmd.extend(extra_args.split())

    # Add skill arguments
    cmd.extend(skill_args)

    print(f"Executing: {' '.join(cmd)}")

    # Execute
    exit_code = subprocess.run(cmd).returncode

    # Save exit code for consolidation
    (results_dir / "exit_code").write_text(str(exit_code))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

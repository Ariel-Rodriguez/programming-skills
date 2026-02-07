#!/usr/bin/env python3
"""
Execute evaluation for a single provider/model combination.

Policy-Mechanism Separation: Configuration passed as parameters.
Single Responsibility: Only runs evaluation, doesn't detect or orchestrate.
"""

import subprocess
import sys
import os
import re
from pathlib import Path


def get_timestamp():
    """
    Get current timestamp for artifact naming.

    Returns:
        Timestamp string in format YYYYMMDD-HHMMSS
    """
    import time
    return time.strftime('%Y%m%d-%H%M%S')


def get_timestamp_iso():
    """
    Get current timestamp in ISO format.

    Returns:
        ISO timestamp string
    """
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')


def extract_model_name(model: str) -> str:
    """
    Extract clean model name for artifact naming.

    Args:
        model: Full model name (e.g., qwen-coder-next:cloud)

    Returns:
        Clean model name (e.g., qwen-coder-next-cloud)
    """
    # Replace : and / with -
    clean = model.replace(":", "-").replace("/", "-")
    # Remove any trailing dots or dashes
    clean = clean.strip("-.")
    return clean


def main():
    if len(sys.argv) < 3:
        print("Usage: run_evaluation.py <provider> <model> [threshold] [extra_args]")
        sys.exit(1)

    provider = sys.argv[1]
    model = sys.argv[2]
    threshold = sys.argv[3] if len(sys.argv) > 3 else "50"
    extra_args = sys.argv[4] if len(sys.argv) > 4 else ""

    # Timestamp for artifact naming
    timestamp = get_timestamp()
    timestamp_iso = get_timestamp_iso()
    model_clean = extract_model_name(model)

    # Results directory with timestamp for historical tracking
    # Format: provider/model-timestamp
    results_dir = Path("tests/results") / provider / f"{model_clean}-{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"==> Running evaluation: {provider}/{model}")
    print(f"    Results: {results_dir}")
    print(f"    Timestamp: {timestamp_iso}")
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
        "--frozen",
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

    print(f"[{provider}/{model}] Executing evaluation...")
    print(f"[{provider}/{model}] Output will be in: {results_dir}")

    # Execute with live output
    exit_code = subprocess.run(cmd).returncode

    if exit_code == 0:
        print(f"[{provider}/{model}] ✅ Evaluation completed successfully")
    else:
        print(f"[{provider}/{model}] ❌ Evaluation failed with exit code {exit_code}")

    # Save exit code and metadata for consolidation
    (results_dir / "exit_code").write_text(str(exit_code))
    (results_dir / "metadata.json").write_text(json.dumps({
        "provider": provider,
        "model": model,
        "timestamp": timestamp_iso,
        "timestamp_epoch": timestamp,
        "model_clean": model_clean
    }, indent=2))

    sys.exit(exit_code)


if __name__ == "__main__":
    import json
    main()

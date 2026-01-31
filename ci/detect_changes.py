#!/usr/bin/env python3
"""
Detect modified skills in a PR.

Outputs space-separated skill names to stdout (for GitHub Actions integration).
"""

import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Error: PR number not provided.", file=sys.stderr)
        print("Usage: detect_changes.py <pr_number>", file=sys.stderr)
        sys.exit(1)

    pr_number = sys.argv[1]

    # Check for GITHUB_TOKEN
    import os
    if not os.environ.get("GITHUB_TOKEN"):
        print("Error: GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    try:
        # Get modified files from PR
        result = subprocess.run(
            ["gh", "pr", "diff", pr_number, "--name-only"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print("", end="")  # Empty output
            return

        # Extract skill names from skills/* paths
        skills = set()
        for line in result.stdout.strip().split("\n"):
            if line.startswith("skills/"):
                skill_name = line.split("/")[1]
                if skill_name:
                    skills.add(skill_name)

        # Output space-separated names
        print(" ".join(sorted(skills)))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

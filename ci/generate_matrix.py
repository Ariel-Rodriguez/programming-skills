#!/usr/bin/env python3
"""
Generate matrix from config with optional skill override.

If skills are provided, creates one matrix item per skill per model.
Otherwise uses orchestrator to detect changed skills.
"""

import subprocess
import json
import sys
from pathlib import Path


def generate_base_matrix(filter_provider: str = "all") -> dict:
    """Generate base matrix from config."""
    result = subprocess.run(
        ["uv", "run", "--with", "pyyaml", "ci/matrix_generator.py", "--filter-provider", filter_provider],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error generating matrix: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Error parsing matrix JSON: {result.stdout}", file=sys.stderr)
        sys.exit(1)


def expand_with_override_skills(base_matrix: dict, skills: list) -> dict:
    """Expand matrix with override skills."""
    matrix = {"include": []}
    
    for item in base_matrix["include"]:
        for skill in skills:
            new_item = item.copy()
            new_item["skill"] = skill
            new_item["display_name"] = f"{item['display_name']} / {skill}"
            matrix["include"].append(new_item)
    
    return matrix


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_matrix.py <pr_number> [skill1 skill2 ...]")
        sys.exit(1)

    pr_number = sys.argv[1]
    override_skills = sys.argv[2:] if len(sys.argv) > 2 else []

    if override_skills:
        # Use override skills
        print(f"Using override skills: {override_skills}", file=sys.stderr)
        base_matrix = generate_base_matrix("all")
        matrix = expand_with_override_skills(base_matrix, override_skills)
    else:
        # Auto-detect from PR
        print(f"Auto-detecting changed skills in PR #{pr_number}", file=sys.stderr)
        result = subprocess.run(
            ["python3", "ci/orchestrate_evaluations.py", str(pr_number), "--matrix-only", "--filter-provider", "all"],
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            print(f"Error detecting changes: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        
        matrix = json.loads(result.stdout)

    # Output matrix
    print(json.dumps(matrix))


if __name__ == "__main__":
    main()

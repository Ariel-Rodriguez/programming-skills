#!/usr/bin/env python3
"""
Consolidate results from parallel evaluations.

Aggregates outputs from multiple provider/model runs and generates summary.
"""

import json
import sys
from pathlib import Path


def main():
    results_base = Path("tests/results")

    print("==> Consolidating results from all evaluations")

    # Find all summary.json files (artifacts download to flat structure)
    summary_files = sorted(results_base.glob("*/summary.json"))

    if not summary_files:
        print(f"No results found in {results_base}")
        print(f"Directory contents: {list(results_base.glob('*'))}")
        # Write empty comment so job doesn't fail
        Path("comment.md").write_text("# Evaluation Results\n\nNo results found.\n")
        sys.exit(0)

    # Check for failures
    failed = 0
    succeeded = 0
    all_results = []

    print("\nResults:")
    print("========")

    for summary_file in summary_files:
        try:
            summary = json.loads(summary_file.read_text())
            artifact_name = summary_file.parent.name
            
            all_results.append({
                "artifact": artifact_name,
                "summary": summary,
            })
            
            print(f"✅ {artifact_name}")
            succeeded += 1
            
        except json.JSONDecodeError:
            print(f"❌ {summary_file.parent.name} - Could not parse JSON")
            failed += 1

    print("\nSummary:")
    print("========")
    print(f"Processed: {len(all_results)}")
    print(f"Failed: {failed}")

    # Generate comment
    comment = "# 📊 Evaluation Results\n\n"
    
    if all_results:
        comment += f"Processed {len(all_results)} evaluation(s).\n\n"
        
        for result in all_results:
            comment += f"## {result['artifact']}\n"
            comment += f"```json\n{json.dumps(result['summary'], indent=2)}\n```\n\n"
    else:
        comment += "No evaluation results found.\n"

    Path("comment.md").write_text(comment)
    print("\n✓ Comment saved to comment.md")
    
    sys.exit(0)


if __name__ == "__main__":
    import os
    main()

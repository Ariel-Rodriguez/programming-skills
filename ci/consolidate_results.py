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

    # Find all result directories
    result_dirs = sorted([d for d in results_base.glob("*/*") if d.is_dir()])

    if not result_dirs:
        print("No results found in tests/results")
        sys.exit(1)

    # Check for failures
    failed = 0
    succeeded = 0
    all_results = []

    print("\nResults by provider/model:")
    print("==========================")

    for result_dir in result_dirs:
        exit_code_file = result_dir / "exit_code"
        if not exit_code_file.exists():
            continue

        try:
            exit_code = int(exit_code_file.read_text().strip())
        except (ValueError, IOError):
            continue

        provider_model = str(result_dir.relative_to(results_base))

        if exit_code == 0:
            print(f"✅ {provider_model} - PASSED")
            succeeded += 1
        else:
            print(f"❌ {provider_model} - FAILED (exit code: {exit_code})")
            failed += 1

        # Collect summary if exists
        summary_file = result_dir / "summary.json"
        if summary_file.exists():
            try:
                summary = json.loads(summary_file.read_text())
                all_results.append({
                    "provider_model": provider_model,
                    "summary": summary,
                })
            except json.JSONDecodeError:
                pass

    print("\nSummary:")
    print("========")
    print(f"Succeeded: {succeeded}")
    print(f"Failed: {failed}")

    # Generate consolidated comment for PR
    pr_number = os.environ.get("PR_NUMBER")
    if pr_number and failed == 0:
        print("\nGenerating consolidated PR comment...")

        comment = f"## 🎉 All Evaluations Passed\n\n"
        comment += f"Tested across {succeeded} provider/model combinations.\n\n"

        for result in all_results:
            comment += f"### Results: {result['provider_model']}\n"
            comment += f"```json\n{json.dumps(result['summary'], indent=2)}\n```\n\n"

        comment_path = Path("comment.md")
        comment_path.write_text(comment)
        print("✓ Consolidated comment saved to comment.md")

    # Exit with failure if any evaluation failed
    if failed > 0:
        print(f"\n❌ {failed} evaluation(s) failed")
        sys.exit(1)

    print("\n✅ All evaluations passed")
    sys.exit(0)


if __name__ == "__main__":
    import os
    main()

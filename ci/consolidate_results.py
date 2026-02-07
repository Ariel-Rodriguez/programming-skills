#!/usr/bin/env python3
"""
Consolidate results from parallel evaluations.

Aggregates outputs from multiple provider/model runs and generates summary.
Supports both PR comments and benchmark dashboard generation.
"""

import argparse
import json
import sys
from pathlib import Path


def generate_pr_comment(results: list) -> str:
    """
    Generate GitHub PR comment from results.

    Args:
        results: List of result dictionaries

    Returns:
        Markdown comment string
    """
    comment = "# 📊 Evaluation Results\n\n"

    if results:
        comment += f"Processed {len(results)} evaluation(s).\n\n"

        # Build table with results
        comment += "| Test Name | Model | Baseline | With Skill | Cases Pass | Winner |\n"
        comment += "|-----------|-------|----------|------------|------------|--------|\n"

        # Rating hierarchy for comparison
        rating_hierarchy = {'vague': 0, 'regular': 1, 'good': 2, 'outstanding': 3}

        for result in results:
            summary = result['summary']
            artifact = result['artifact']

            # Extract key data from nested results[0]
            eval_result = summary.get('results', [{}])[0] if summary.get('results') else {}

            skill = eval_result.get('skill', 'N/A')
            model = eval_result.get('model', 'N/A')
            baseline_rating = eval_result.get('baseline_rating', 'N/A')
            skill_rating = eval_result.get('skill_rating', 'N/A')
            baseline_pass = eval_result.get('baseline_pass_count', 'N/A')
            skill_pass = eval_result.get('skill_pass_count', 'N/A')
            overall_better = eval_result.get('judgment', {}).get('overall_better', 'N/A')

            # Determine winner
            if overall_better == 'A':
                winner = "Baseline"
            elif overall_better == 'B':
                winner = "With Skill"
            elif overall_better == 'TIE':
                winner = "Tie"
            else:
                winner = "N/A"

            # Determine emoji for cases pass
            baseline_score = rating_hierarchy.get(baseline_rating, -1)
            skill_score = rating_hierarchy.get(skill_rating, -1)
            pass_emoji = "✅" if skill_score >= baseline_score else "❌"

            # Build row
            test_link = f"[{artifact}]()"
            comment += f"| {test_link} | {model} | {baseline_rating} | {skill_rating} | {pass_emoji} {skill_pass} | {winner} |\n"

        comment += "\n"
    else:
        comment += "No evaluation results found.\n"

    return comment


def generate_benchmark_data(results: list, output_dir: Path) -> None:
    """
    Generate benchmark data files for dashboard.

    Args:
        results: List of result dictionaries
        output_dir: Directory to write benchmark data
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for result in results:
        summary = result['summary']
        artifact = result['artifact']

        # Save individual benchmark data
        benchmark_file = output_dir / f"{artifact}.json"
        benchmark_file.write_text(json.dumps(summary, indent=2))

    # Save aggregated data for dashboard
    aggregated = {
        "generated_at": json.dumps(None),  # Will be set by generate_dashboard_data.py
        "results": [
            {
                "artifact": r['artifact'],
                "summary": r['summary']
            }
            for r in results
        ]
    }

    aggregated_file = output_dir / "benchmark_aggregated.json"
    aggregated_file.write_text(json.dumps(aggregated, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Consolidate evaluation results")
    parser.add_argument("--mode", choices=["pr-comment", "benchmark"], default="pr-comment",
                       help="Output mode: pr-comment or benchmark")
    parser.add_argument("--results-dir", type=Path, default="tests/results",
                       help="Directory containing evaluation results")
    parser.add_argument("--output-dir", type=Path, default=None,
                       help="Output directory for benchmark mode")
    parser.add_argument("--output-file", type=Path, default="comment.md",
                       help="Output file for PR comment mode")
    args = parser.parse_args()

    if args.mode == "benchmark" and not args.output_dir:
        args.output_dir = args.results_dir / "benchmark"

    print(f"==> Consolidating results (mode: {args.mode})")

    # Find all summary.json files
    summary_files = sorted(args.results_dir.glob("*/summary.json"))

    if not summary_files:
        print(f"No results found in {args.results_dir}")
        print(f"Directory contents: {list(args.results_dir.glob('*'))}")

        if args.mode == "pr-comment":
            Path(args.output_file).write_text("# Evaluation Results\n\nNo results found.\n")
        sys.exit(0)

    # Process results
    all_results = []
    failed = 0

    for summary_file in summary_files:
        try:
            summary = json.loads(summary_file.read_text())
            artifact_name = summary_file.parent.name

            all_results.append({
                "artifact": artifact_name,
                "summary": summary,
            })

            print(f"✅ {artifact_name}")

        except json.JSONDecodeError as e:
            print(f"❌ {summary_file.parent.name} - Could not parse JSON: {e}")
            failed += 1

    print(f"\nSummary:")
    print(f"  Processed: {len(all_results)}")
    print(f"  Failed: {failed}")

    # Generate output based on mode
    if args.mode == "pr-comment":
        comment = generate_pr_comment(all_results)
        args.output_file.write_text(comment)
        print(f"\n✓ Comment saved to {args.output_file}")

    elif args.mode == "benchmark":
        generate_benchmark_data(all_results, args.output_dir)
        print(f"\n✓ Benchmark data saved to {args.output_dir}")

    sys.exit(0)


if __name__ == "__main__":
    main()

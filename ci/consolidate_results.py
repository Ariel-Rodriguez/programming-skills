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
        
        # Build table with results
        comment += "| Test Name | Model | Baseline | With Skill | Cases Pass | Winner |\n"
        comment += "|-----------|-------|----------|------------|------------|--------|\n"
        
        # Rating hierarchy for comparison
        rating_hierarchy = {'vague': 0, 'regular': 1, 'good': 2, 'outstanding': 3}
        
        for result in all_results:
            summary = result['summary']
            artifact = result['artifact']
            
            # Debug: Log top-level keys
            print(f"\n📋 Processing: {artifact}")
            print(f"   Top-level keys: {list(summary.keys())}")
            
            # Extract key data from nested results[0]
            eval_result = summary.get('results', [{}])[0] if summary.get('results') else {}
            print(f"   Nested result keys: {list(eval_result.keys())}")
            
            skill = eval_result.get('skill', 'N/A')
            model = eval_result.get('model', 'N/A')
            baseline_rating = eval_result.get('baseline_rating', 'N/A')
            skill_rating = eval_result.get('skill_rating', 'N/A')
            baseline_pass = eval_result.get('baseline_pass_count', 'N/A')
            skill_pass = eval_result.get('skill_pass_count', 'N/A')
            overall_better = eval_result.get('judgment', {}).get('overall_better', 'N/A')
            
            print(f"   Extracted: model={model}, baseline={baseline_rating}, skill={skill_rating}, winner={overall_better}")
            
            # Determine winner
            if overall_better == 'A':
                winner = "Baseline"
            elif overall_better == 'B':
                winner = "With Skill"
            elif overall_better == 'TIE':
                winner = "Tie"
            else:
                winner = "N/A"
            
            # Determine emoji for cases pass (skill >= baseline in rating hierarchy)
            baseline_score = rating_hierarchy.get(baseline_rating, -1)
            skill_score = rating_hierarchy.get(skill_rating, -1)
            pass_emoji = "✅" if skill_score >= baseline_score else "❌"
            
            # Build row
            test_link = f"[{artifact}]()"
            comment += f"| {test_link} | {model} | {baseline_rating} | {skill_rating} | {pass_emoji} {skill_pass} | {winner} |\n"
        
        comment += "\n"
    else:
        comment += "No evaluation results found.\n"

    Path("comment.md").write_text(comment)
    print("\n✓ Comment saved to comment.md")
    
    sys.exit(0)


if __name__ == "__main__":
    import os
    main()

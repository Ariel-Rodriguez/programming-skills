#!/usr/bin/env python3
"""
Dynamic Benchmark Harness - Refactored

Composition Root: Wires together domain, ports, adapters, and services.

Applied Skills:
- Functional Core, Imperative Shell: Pure logic in domain/, IO in adapters/
- Explicit State Invariants: Immutable domain types with explicit states
- Single Direction Data Flow: Clear data ownership, unidirectional flow
- Local Reasoning: Dependencies explicit, no hidden globals
- Naming as Design: Intent-revealing module and function names
- Policy-Mechanism Separation: Business rules in domain, execution in services
- Error Handling Design: Result types instead of exceptions
- Minimize Mutation: Immutable data structures throughout
- Explicit Boundaries: Ports separate domain from infrastructure
- Composition Over Coordination: Services compose small focused units
"""

import argparse
import sys
from pathlib import Path

# Domain imports
from domain import Provider, ModelConfig, is_failure, is_success

# Service imports
from services import (
    discover_skills,
    generate_test_suite,
    run_evaluation,
    save_summary,
    generate_console_report,
    generate_github_comment,
)

# Adapter imports
from adapters import RealFileSystem, OllamaAdapter, CopilotCLIAdapter


def main() -> int:
    """
    Main entry point - Composition Root.
    
    Composition Over Coordination: Wires dependencies at startup.
    Single Direction Data Flow: Clear pipeline of operations.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Skill Benchmark Harness (Refactored with Programming Skills)"
    )
    parser.add_argument("--skill", action="append", help="Test specific skill(s)")
    parser.add_argument("--all", action="store_true", help="Test all skills")
    parser.add_argument("--model", help="Model to use (default: llama3.2:latest)")
    parser.add_argument(
        "--provider",
        choices=["ollama", "copilot"],
        default="ollama",
        help="Model provider"
    )
    parser.add_argument("--threshold", type=int, default=50, help="Minimum pass rate threshold (default: 50)")
    parser.add_argument("--report", action="store_true", help="Generate console report")
    parser.add_argument("--github-comment", action="store_true", help="Generate comment.md for PRs")
    parser.add_argument("--judge", action="store_true", help="Use LLM judge for semantic evaluation")
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    args = parser.parse_args()
    
    # Wire up adapters (Dependency Injection)
    fs = RealFileSystem()
    
    # Configuration (Policy)
    skills_dir = Path("skills")
    results_dir = Path("tests/results")
    summary_path = results_dir / "summary.json"
    model_name = args.model or "llama3.2:latest"
    provider = Provider.OLLAMA if args.provider == "ollama" else Provider.COPILOT
    
    # Handle report-only modes
    if args.report and not args.all and not args.skill:
        print(generate_console_report(summary_path, fs))
        return 0
    
    if args.github_comment and not args.all and not args.skill:
        result = generate_github_comment(summary_path, fs)
        if is_success(result):
            write_result = fs.write_text(Path("comment.md"), result.value)
            if is_success(write_result):
                print("\n[OK] PR comment generated in comment.md")
                return 0
            else:
                print(f"Error writing comment.md: {write_result.error_message}")
                return 1
        else:
            print(f"Error generating comment: {result.error_message}")
            return 1
    
    # Model configuration
    config = ModelConfig(
        provider=provider,
        model_name=model_name,
        base_url="http://localhost:11434/v1",
        num_ctx=64000
    )
    
    # Select model adapter based on provider
    model_port = OllamaAdapter() if provider == Provider.OLLAMA else CopilotCLIAdapter()
    
    # Discover skills
    all_skills = discover_skills(skills_dir, fs)
    
    if not all_skills:
        print(f"No skills found in {skills_dir}")
        return 1
    
    # Filter skills to test
    skills_to_test = all_skills
    if args.skill:
        skills_to_test = tuple(
            s for s in all_skills
            if any(name in s.name for name in args.skill)
        )
        if not skills_to_test:
            print(f"No matching skills found")
            return 1
    
    # Check model availability
    if provider == Provider.OLLAMA:
        if not model_port.is_available(config):
            print(f"Error: Ollama not running at {config.base_url}")
            print("Start with: ollama serve")
            return 1
    
    # Create results directory
    result = fs.mkdir(results_dir)
    if is_failure(result):
        print(f"Warning: Could not create results directory: {result.error_message}")
    
    # Run evaluations
    print(f"\n{'=' * 60}")
    print(f"Model: {config.model_name} | Provider: {config.provider.value}")
    print(f"{'=' * 60}")
    
    all_results = []
    
    for skill in skills_to_test:
        print(f"\nTesting: {skill.name}")
        print("-" * 40)
        
        # Generate test suite
        test_suite = generate_test_suite(skill, fs)
        print(f"  Generated {test_suite.test_count} test cases")
        
        # Run evaluation
        eval_result = run_evaluation(
            skill, test_suite, model_port, config, args.verbose, args.judge
        )
        all_results.append(eval_result)
        
        # Display results
        if eval_result.judgment:
            judge = eval_result.judgment
            print(
                f"  Baseline: {eval_result.baseline_pass_rate}% | "
                f"With Skill: {eval_result.skill_pass_rate}% | "
                f"Improvement: {eval_result.improvement:+}%"
            )
            print(f"  🤖 Judge: {judge.vs_baseline} (score: {judge.score}/100)")
            print(f"     {judge.reasoning}")
        else:
            print(
                f"  Baseline: {eval_result.baseline_pass_rate}% | "
                f"With Skill: {eval_result.skill_pass_rate}% | "
                f"Improvement: {eval_result.improvement:+}%"
            )
    
    # Save summary
    save_result = save_summary(tuple(all_results), summary_path, fs)
    
    if is_failure(save_result):
        print(f"\nWarning: Failed to save summary: {save_result.error_message}")
    else:
        print(f"\n{'=' * 60}")
        print(f"Complete. Summary saved to: {summary_path}")
    
    # Generate reports if requested
    if args.report:
        print(f"\n{generate_console_report(summary_path, fs)}")
    
    if args.github_comment:
        result = generate_github_comment(summary_path, fs)
        if is_success(result):
            write_result = fs.write_text(Path("comment.md"), result.value)
            if is_success(write_result):
                print("\n[OK] PR comment generated in comment.md")
            else:
                print(f"Error writing comment.md: {write_result.error_message}")
        else:
            print(f"Error generating comment: {result.error_message}")
    
    # Check threshold - use judgment when available
    failed_skills = []
    for r in all_results:
        # If we have a judgment, use it instead of mechanical threshold
        if r.judgment:
            if not r.judgment.is_improvement:
                failed_skills.append(r.skill_name)
        else:
            # Fall back to mechanical threshold
            if r.skill_pass_rate < args.threshold:
                failed_skills.append(r.skill_name)
    
    if failed_skills:
        print(f"\n[FAIL] {len(failed_skills)} skills failed threshold: {', '.join(failed_skills)}")
        
        # Debug info: show what went wrong
        print("\nDEBUG - Failure details:")
        for r in all_results:
            if r.skill_name in failed_skills:
                print(f"\n  {r.skill_name}:")
                print(f"    Baseline: {r.baseline_pass_rate}% ({sum(1 for t in r.baseline_results if t.passed)}/{len(r.baseline_results)} passed)")
                print(f"    With Skill: {r.skill_pass_rate}% ({sum(1 for t in r.skill_results if t.passed)}/{len(r.skill_results)} passed)")
                
                if r.judgment:
                    print(f"    Judge: {r.judgment.vs_baseline} (score: {r.judgment.score}/100)")
                    print(f"    Reasoning: {r.judgment.reasoning}")
                
                # Show test failures
                for baseline, skill in zip(r.baseline_results, r.skill_results):
                    if not baseline.passed or not skill.passed:
                        print(f"    Test: {baseline.test_name}")
                        if not baseline.passed:
                            print(f"      Baseline FAIL: {baseline.failure_reason[:100]}")
                        if not skill.passed:
                            print(f"      Skill FAIL: {skill.failure_reason[:100]}")
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Reporting Service

Single Responsibility: Saves evaluation results and generates reports.
"""

import json
import time
from pathlib import Path
from domain import EvaluationResult, Result, Success, Failure
from ports import FileSystemPort


def save_summary(
    results: tuple[EvaluationResult, ...],
    output_path: Path,
    fs: FileSystemPort
) -> Result:
    """
    Save evaluation results summary to JSON.
    
    Minimize Mutation: Builds new structure, doesn't modify input.
    Local Reasoning: All dependencies explicit.
    
    Args:
        results: Evaluation results to save
        output_path: Where to save summary
        fs: Filesystem port
        
    Returns:
        Success or Failure result
    """
    # Build summary structure (immutable transformation)
    summary = {
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
        "results": [
            _serialize_evaluation_result(result)
            for result in results
        ]
    }
    
    # Convert to JSON
    content = json.dumps(summary, indent=2)
    
    # Write to file
    return fs.write_text(output_path, content)


def generate_console_report(summary_path: Path, fs: FileSystemPort) -> str:
    """
    Generate console report from summary.json.
    
    Pure function (with IO via port): Reads summary, generates markdown table.
    
    Args:
        summary_path: Path to summary.json
        fs: Filesystem port
        
    Returns:
        Markdown formatted report string
    """
    if not fs.exists(summary_path):
        return "No summary file found. Run a benchmark first."
    
    result = fs.read_text(summary_path)
    if isinstance(result, Failure):
        return f"Error reading summary: {result.error_message}"
    
    try:
        data = json.loads(result.value)
        results = data.get('results', [])
        
        lines = ["# Benchmark Results", ""]
        
        # Check if any result has judgment data
        has_judgments = any(r.get('judgment') for r in results)
        
        if has_judgments:
            lines.append("| Skill | Severity | Model | Baseline | With Skill | Improvement | Judge Score | Status |")
            lines.append("|-------|----------|-------|----------|------------|-------------|-------------|--------|")
        else:
            lines.append("| Skill | Severity | Model | Baseline | With Skill | Improvement | Status |")
            lines.append("|-------|----------|-------|----------|------------|-------------|--------|")
        
        for r in results:
            baseline = r.get('baseline_rate', 0)
            skill = r.get('skill_rate', 0)
            improvement = r.get('improvement', 0)
            severity = r.get('severity', 'SUGGEST')
            judgment = r.get('judgment')
            
            # Determine status - prefer judgment over mechanical
            if judgment:
                score = judgment.get('score', 0)
                vs_baseline = judgment.get('vs_baseline', 'Same')
                if vs_baseline == 'Better':
                    status = "✅"
                elif vs_baseline == 'Worse':
                    status = "❌"
                else:
                    status = "~"
                judge_str = f"{score}/100 ({vs_baseline})"
            else:
                status = "+" if improvement > 0 else ("-" if improvement < 0 else "~")
                judge_str = "N/A"
            
            imp_str = f"{improvement:+}%"
            
            if has_judgments:
                lines.append(
                    f"| {r['skill']} | {severity} | {r['model']} | "
                    f"{baseline}% | {skill}% | {imp_str} | {judge_str} | {status} |"
                )
            else:
                lines.append(
                    f"| {r['skill']} | {severity} | {r['model']} | "
                    f"{baseline}% | {skill}% | {imp_str} | {status} |"
                )
        
        return "\n".join(lines)
    except json.JSONDecodeError as e:
        return f"Error parsing summary JSON: {e}"
    except Exception as e:
        return f"Error generating report: {e}"


def generate_github_comment(summary_path: Path, fs: FileSystemPort) -> Result:
    """
    Generate detailed GitHub PR comment from summary.json.
    
    Args:
        summary_path: Path to summary.json
        fs: Filesystem port
        
    Returns:
        Success(markdown_string) or Failure
    """
    if not fs.exists(summary_path):
        return Failure("No summary file found", {})
    
    result = fs.read_text(summary_path)
    if isinstance(result, Failure):
        return result
    
    try:
        data = json.loads(result.value)
        results = data.get('results', [])
        
        lines = ["## [SKILL EVALUATION] Results", ""]
        
        # Check if we have judgment data
        has_judgments = any(r.get('judgment') for r in results)
        
        if has_judgments:
            lines.append("| Skill | Status | Baseline | With Skill | Improvement | Judge Verdict |")
            lines.append("|-------|--------|----------|------------|-------------|---------------|")
        else:
            lines.append("| Skill | Status | Baseline | With Skill | Improvement |")
            lines.append("|-------|--------|----------|------------|-------------|")
        
        for r in results:
            baseline = r.get('baseline_rate', 0)
            skill = r.get('skill_rate', 0)
            improvement = r.get('improvement', 0)
            judgment = r.get('judgment')
            
            # Determine status - prefer judgment
            if judgment:
                vs_baseline = judgment.get('vs_baseline', 'Same')
                score = judgment.get('score', 0)
                if vs_baseline == 'Better':
                    status = "✅"
                elif vs_baseline == 'Worse':
                    status = "❌"
                else:
                    status = "~"
                judge_verdict = f"{vs_baseline} ({score}/100)"
            else:
                status = "+" if improvement > 0 else ("-" if improvement < 0 else "~")
                judge_verdict = "N/A"
            
            if has_judgments:
                lines.append(f"| {r['skill']} | {status} | {baseline}% | {skill}% | {improvement:+}% | {judge_verdict} |")
            else:
                lines.append(f"| {r['skill']} | {status} | {baseline}% | {skill}% | {improvement:+}% |")
        
        lines.append("\n---")
        
        # Add judgment reasoning if available
        for r in results:
            judgment = r.get('judgment')
            if judgment:
                lines.append(f"\n### 🤖 LLM Judge: {r['skill']}")
                lines.append(f"**Follows Principle:** {judgment.get('follows_principle', 'Unknown')}")
                lines.append(f"**vs Baseline:** {judgment.get('vs_baseline', 'Unknown')}")
                lines.append(f"**Score:** {judgment.get('score', 0)}/100")
                lines.append(f"\n**Reasoning:** {judgment.get('reasoning', 'No reasoning provided')}")
                lines.append("")
        
        lines.append("\n---")
        lines.append("\n### [DEBUG] Detailed Info")
        
        for r in results:
            lines.append(f"\n<details>")
            lines.append(f"<summary><b>{r['skill']}</b> ({r.get('skill_rate', 0)}% pass rate)</summary>\n")
            
            for test in r.get('results', []):
                test_status = "[PASS]" if test['skill']['pass'] else "[FAIL]"
                lines.append(f"\n#### {test_status} {test['name']}")
                lines.append("\n**AI Generated Code:**")
                lines.append(f"\n```javascript")
                lines.append(test['skill']['response_full'])
                lines.append("```")
            
            lines.append("\n</details>")
        
        return Success("\n".join(lines))
    except json.JSONDecodeError as e:
        return Failure(f"Invalid JSON in summary", {"error": str(e)})
    except Exception as e:
        return Failure(f"Error generating GitHub comment", {"error": str(e)})


def _serialize_evaluation_result(result: EvaluationResult) -> dict:
    """
    Serialize EvaluationResult to dictionary.
    
    Pure function: Data transformation only.
    
    Args:
        result: Evaluation result
        
    Returns:
        Dictionary representation
    """
    serialized = {
        "skill": result.skill_name,
        "severity": result.severity.value,
        "model": result.model,
        "baseline_rate": result.baseline_pass_rate,
        "skill_rate": result.skill_pass_rate,
        "improvement": result.improvement,
        "results": [
            {
                "name": baseline.test_name,
                "baseline": {
                    "pass": baseline.passed,
                    "response_preview": baseline.response_preview,
                    "response_full": baseline.response
                },
                "skill": {
                    "pass": skill.passed,
                    "response_preview": skill.response_preview,
                    "response_full": skill.response
                }
            }
            for baseline, skill in zip(result.baseline_results, result.skill_results)
        ]
    }
    
    # Add judgment if present
    if result.judgment:
        serialized["judgment"] = {
            "follows_principle": result.judgment.follows_principle,
            "vs_baseline": result.judgment.vs_baseline,
            "score": result.judgment.score,
            "reasoning": result.judgment.reasoning
        }
    
    return serialized

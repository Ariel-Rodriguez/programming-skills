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


def save_history(
    results: tuple[EvaluationResult, ...],
    history_dir: Path,
    provider: str,
    timestamp_id: str,
    timestamp_iso: str,
    fs: FileSystemPort
) -> Result:
    """
    Save per-skill history files for a benchmark run.

    Args:
        results: Evaluation results to save
        history_dir: Base history directory
        provider: Provider name
        timestamp: Timestamp string (YYYYMMDD-HHMMSS)
        fs: Filesystem port

    Returns:
        Success or Failure result
    """
    def _clean_name(value: str) -> str:
        return value.replace("/", "-").replace(":", "-")

    for result in results:
        skill_dir = history_dir / result.skill_name
        fs.mkdir(skill_dir)

        model_clean = _clean_name(result.model)
        filename = f"{model_clean}-{timestamp_id}.json"
        output_path = skill_dir / filename

        payload = _serialize_evaluation_result(result)
        payload["timestamp"] = timestamp_iso
        payload["skill"] = result.skill_name
        payload["provider"] = provider

        content = json.dumps(payload, indent=2)
        write_result = fs.write_text(output_path, content)
        if isinstance(write_result, Failure):
            return write_result

    return Success("ok")


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
            lines.append("| Skill | Severity | Model | Baseline | With Skill | Improvement | Cases Pass (n/n) | Judge Score | Status |")
            lines.append("|-------|----------|-------|----------|------------|-------------|------------------|-------------|--------|")
        else:
            lines.append("| Skill | Severity | Model | Baseline | With Skill | Improvement | Cases Pass (n/n) | Status |")
            lines.append("|-------|----------|-------|----------|------------|-------------|------------------|--------|")
        
        for r in results:
            baseline = r.get('baseline_rating', 'vague')
            skill = r.get('skill_rating', 'vague')
            baseline_count = r.get('baseline_pass_count', "0/0")
            skill_count = r.get('skill_pass_count', "0/0")
            pass_counts = f"{baseline_count} -> {skill_count}"
            
            improvement = r.get('improvement', 0)
            severity = r.get('severity', 'SUGGEST')
            judgment = r.get('judgment')
            
            # Determine status - prefer judgment over mechanical
            if judgment:
                score = judgment.get('score', 0)
                overall_better = judgment.get('overall_better', 'Equal')
                if overall_better == 'B':  # B is skill-enhanced
                    status = "✅"
                    imp_str = "yes"
                elif overall_better == 'A':  # A is baseline (worse)
                    status = "❌"
                    imp_str = "no"
                else:
                    status = "~"
                    imp_str = "neutral"
                judge_str = f"{score}/100 ({overall_better})"
            else:
                status = "+" if improvement > 0 else ("-" if improvement < 0 else "~")
                judge_str = "N/A"
                imp_str = f"{improvement:+}%"
            
            if has_judgments:
                lines.append(
                    f"| {r['skill']} | {severity} | {r['model']} | "
                    f"{baseline} | {skill} | {imp_str} | {pass_counts} | {judge_str} | {status} |"
                )
            else:
                lines.append(
                    f"| {r['skill']} | {severity} | {r['model']} | "
                    f"{baseline} | {skill} | {imp_str} | {pass_counts} | {status} |"
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
            lines.append("| Skill | Status | Baseline | With Skill | Improvement | Cases Pass (n/n) | Judge Verdict |")
            lines.append("|-------|--------|----------|------------|-------------|------------------|---------------|")
        else:
            lines.append("| Skill | Status | Baseline | With Skill | Improvement | Cases Pass (n/n) |")
            lines.append("|-------|--------|----------|------------|-------------|------------------|")
        
        for r in results:
            baseline = r.get('baseline_rating', 'vague')
            skill = r.get('skill_rating', 'vague')
            baseline_count = r.get('baseline_pass_count', "0/0")
            skill_count = r.get('skill_pass_count', "0/0")
            pass_counts = f"{baseline_count} -> {skill_count}"
            
            improvement = r.get('improvement', 0)
            judgment = r.get('judgment')
            
            # Determine status - prefer judgment
            if judgment:
                overall_better = judgment.get('overall_better', 'Equal')
                score = judgment.get('score', 0)
                if overall_better == 'B':  # B is skill version
                    status = "✅"
                    improvement_label = "yes"
                elif overall_better == 'A':  # A is baseline
                    status = "❌"
                    improvement_label = "no"
                else:
                    status = "~"
                    improvement_label = "neutral"
                judge_verdict = f"{overall_better} ({score}/100)"
            else:
                status = "+" if improvement > 0 else ("-" if improvement < 0 else "~")
                improvement_label = f"{improvement:+}%"
                judge_verdict = "N/A"
            
            if has_judgments:
                lines.append(f"| {r['skill']} | {status} | {baseline} | {skill} | {improvement_label} | {pass_counts} | {judge_verdict} |")
            else:
                lines.append(f"| {r['skill']} | {status} | {baseline} | {skill} | {improvement_label} | {pass_counts} |")
        
        lines.append("\n---")
        
        # Add judgment reasoning if available
        for r in results:
            judgment = r.get('judgment')
            if judgment:
                lines.append(f"\n### 🤖 LLM Judge: {r['skill']}")
                lines.append(f"**Principle Adherence:** {judgment.get('principle_better', 'Unknown')}")
                lines.append(f"**Code Quality:** {judgment.get('quality_better', 'Unknown')}")
                lines.append(f"**Overall Better:** {judgment.get('overall_better', 'Unknown')}")
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
        "skill_version": result.skill_version,
        "baseline_rate": result.baseline_pass_rate,
        "skill_rate": result.skill_pass_rate,
        "baseline_rating": result.baseline_rating,
        "skill_rating": result.skill_rating,
        "baseline_pass_count": result.baseline_pass_count,
        "skill_pass_count": result.skill_pass_count,
        "improvement": result.improvement,
        "judge_error": result.judge_error,
        "results": [
            {
                "name": baseline.test_name,
                "input": baseline.input,
                "expected": baseline.expected,
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
            "principle_better": result.judgment.principle_better,
            "quality_better": result.judgment.quality_better,
            "overall_better": result.judgment.overall_better,
            "option_a_rating": result.judgment.option_a_rating,
            "option_b_rating": result.judgment.option_b_rating,
            "score": result.judgment.score,
            "reasoning": result.judgment.reasoning
        }
    
    return serialized

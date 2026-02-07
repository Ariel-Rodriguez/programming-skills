"""
Generate Dashboard Data - Pure Function

Extracts structured data from evaluation JSON files for dashboard rendering.
This is a pure function - no side effects.
"""

import json
import re
from pathlib import Path


def extract_judgment_reasoning(judgment: dict) -> str:
    """
    Extract judgment reasoning with code examples.

    The judgment contains reasoning text. We want to extract key insights
    and highlight code that demonstrates the skill application.

    Args:
        judgment: Judgment dictionary from evaluation results

    Returns:
        Formatted reasoning string with code references
    """
    reasoning = judgment.get('reasoning', 'No reasoning provided')

    # Add rating context
    a_rating = judgment.get('option_a_rating', 'unknown')
    b_rating = judgment.get('option_b_rating', 'unknown')

    context = f"Baseline rated: {a_rating} | With Skill rated: {b_rating}\n\n"

    return context + reasoning


def extract_code_from_test_results(test_results: list, provider: str) -> tuple[str, str]:
    """
    Extract before/after code from test results.

    For provider-specific code extraction:
    - Ollama responses are typically raw code
    - Copilot responses may have markdown formatting

    Args:
        test_results: List of test result dictionaries
        provider: The provider name for formatting

    Returns:
        Tuple of (before_code, after_code) as strings
    """
    before_parts = []
    after_parts = []

    for test in test_results:
        # Extract before code (baseline)
        baseline = test.get('baseline', {})
        before_response = baseline.get('response_full', '')
        if before_response:
            before_parts.append(f"// Test: {test.get('name', 'unknown')}\n{before_response}")

        # Extract after code (skill)
        skill = test.get('skill', {})
        after_response = skill.get('response_full', '')
        if after_response:
            after_parts.append(f"// Test: {test.get('name', 'unknown')}\n{after_response}")

    before_code = "\n\n".join(before_parts) if before_parts else "// No code generated"
    after_code = "\n\n".join(after_parts) if after_parts else "// No code generated"

    return before_code, after_code


def normalize_rating(rating: str) -> str:
    """
    Normalize rating values to consistent format.

    Args:
        rating: Raw rating string

    Returns:
        Normalized rating string
    """
    if not rating:
        return "vague"

    rating = str(rating).lower().strip()

    valid_ratings = ["vague", "regular", "good", "outstanding"]
    if rating in valid_ratings:
        return rating

    # Map numeric values
    if rating in ["0", "1", "2", "3"]:
        mapping = {"0": "vague", "1": "regular", "2": "good", "3": "outstanding"}
        return mapping[rating]

    return "vague"


def _normalize_timestamp(timestamp: str) -> str:
    """
    Normalize timestamp to ISO format (YYYY-MM-DDTHH:MM:SS).
    """
    if not timestamp:
        return ''

    iso_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(Z)?$', timestamp)
    if iso_match:
        return f"{iso_match.group(1)}-{iso_match.group(2)}-{iso_match.group(3)}T{iso_match.group(4)}:{iso_match.group(5)}:{iso_match.group(6)}"

    compact_match = re.match(r'^(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})$', timestamp)
    if compact_match:
        return f"{compact_match.group(1)}-{compact_match.group(2)}-{compact_match.group(3)}T{compact_match.group(4)}:{compact_match.group(5)}:{compact_match.group(6)}"

    dashed_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})T(\d{2})-(\d{2})-(\d{2})$', timestamp)
    if dashed_match:
        return f"{dashed_match.group(1)}-{dashed_match.group(2)}-{dashed_match.group(3)}T{dashed_match.group(4)}:{dashed_match.group(5)}:{dashed_match.group(6)}"

    return timestamp


def _benchmark_id_from_parts(provider: str, model: str, timestamp: str, fallback_stamp: str | None) -> str:
    stamp = _normalize_timestamp(timestamp)
    if stamp and "T" in stamp:
        stamp = stamp.replace(":", "").replace("-", "").replace("T", "-")
        stamp = stamp[:15]
    if not stamp and fallback_stamp:
        stamp = fallback_stamp
    
    # Sanitize model name for Windows paths (no colons)
    safe_model = str(model).replace(":", "-")
    return f"{provider}-{safe_model}-{stamp or 'unknown'}"


def collect_all_benchmarks(history_dir: Path) -> list[dict]:
    """
    Collect all benchmark data from a directory of per-skill history files.

    Args:
        history_dir: Directory containing per-skill history JSON files

    Returns:
        List of structured benchmark data
    """
    if not history_dir.exists():
        return []

    benchmarks_map: dict[tuple[str, str, str], dict] = {}

    for skill_file in history_dir.glob('**/*.json'):
        if skill_file.name.startswith("summary-"):
            continue
        try:
            data = json.loads(skill_file.read_text())
        except Exception:
            continue

        skill_name = data.get('skill', skill_file.parent.name)
        model = data.get('model', 'unknown')
        provider = data.get('provider', 'unknown')
        timestamp = _normalize_timestamp(data.get('timestamp', ''))

        if provider == 'unknown':
            if 'sonnet' in str(model).lower():
                provider = 'copilot'
            elif 'gpt' in str(model).lower():
                provider = 'codex'

        fallback_stamp = None
        match = re.search(r'(\d{8}-\d{6})', skill_file.stem)
        if match:
            fallback_stamp = match.group(1)

        key = (provider, model, timestamp or fallback_stamp or 'unknown')
        benchmark_id = _benchmark_id_from_parts(provider, model, timestamp, fallback_stamp)

        benchmark = benchmarks_map.get(key)
        if not benchmark:
            benchmark = {
                'benchmark_id': benchmark_id,
                'timestamp': timestamp,
                'provider': provider,
                'model': model,
                'skills': []
            }
            benchmarks_map[key] = benchmark

        judgment = data.get('judgment', {})
        test_results = data.get('results', [])
        before_code, after_code = extract_code_from_test_results(test_results, provider)

        overall_better = judgment.get('overall_better') if judgment else None
        if overall_better in ('A', 'B', 'Equal'):
            if overall_better == 'B':
                improvement = 'yes'
            elif overall_better == 'A':
                improvement = 'no'
            else:
                improvement = 'neutral'
        else:
            improvement = data.get('improvement')
            if isinstance(improvement, (int, float)):
                improvement = 'yes' if improvement > 0 else ('no' if improvement < 0 else 'neutral')
            elif improvement is None:
                improvement = 'neutral'

        skill_data = {
            'skill_name': skill_name,
            'provider': provider,
            'model': model,
            'timestamp': timestamp,
            'baseline_rating': normalize_rating(judgment.get('option_a_rating', data.get('baseline_rating', ''))),
            'skill_rating': normalize_rating(judgment.get('option_b_rating', data.get('skill_rating', ''))),
            'improvement': improvement,
            'reasoning': extract_judgment_reasoning(judgment) if judgment else 'No reasoning provided',
            'before_code': before_code,
            'after_code': after_code,
            'judgment': judgment
        }
        benchmark['skills'].append(skill_data)

    all_data = list(benchmarks_map.values())
    all_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return all_data


def _write_per_run_data(output_dir: Path, benchmarks: list[dict]) -> None:
    """
    Write per-run data.json for each benchmark.
    """
    for benchmark in benchmarks:
        benchmark_id = benchmark.get("benchmark_id", "unknown")
        per_run = build_aggregated_data([benchmark])
        output_file = output_dir / "data" / benchmark_id / "data.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(per_run, f, indent=2)


def build_aggregated_data(benchmarks: list[dict]) -> dict:
    """
    Build aggregated data from individual benchmarks.

    Args:
        benchmarks: List of benchmark data

    Returns:
        Aggregated data dict
    """
    if not benchmarks:
        return {'benchmarks': [], 'summary': {}}

    # Collect all skills with unique names
    skill_names = set()
    provider_models = set()

    for benchmark in benchmarks:
        for skill in benchmark.get('skills', []):
            skill_names.add(skill.get('skill_name', 'unknown'))
        provider_models.add((benchmark.get('provider', ''), benchmark.get('model', '')))

    # Count improvements
    total_skills = 0
    improvements = 0
    regressions = 0
    neutral = 0

    for benchmark in benchmarks:
        for skill in benchmark.get('skills', []):
            total_skills += 1
            if skill.get('improvement') == 'yes':
                improvements += 1
            elif skill.get('improvement') == 'no':
                regressions += 1
            else:
                neutral += 1

    # Build summary
    summary = {
        'total_benchmarks': len(benchmarks),
        'total_skills': total_skills,
        'improvements': improvements,
        'regressions': regressions,
        'neutral': neutral,
        'improvement_rate': round((improvements / total_skills * 100) if total_skills > 0 else 0, 1)
    }

    return {
        'benchmarks': benchmarks,
        'summary': summary,
        'unique_skills': sorted(list(skill_names)),
        'provider_models': sorted(list(provider_models))
    }


def generate_dashboard_data(history_dir: Path, output_dir: Path) -> bool:
    """
    Main function: Generate dashboard data from benchmark files.

    Pure function - only reads from history_dir, writes to output_dir.

    Args:
        history_dir: Directory containing per-skill history JSON files
        output_dir: Output directory for benchmarks.json and data/*

    Returns:
        True if successful, False otherwise
    """
    try:
        # Collect all benchmarks
        benchmarks = collect_all_benchmarks(history_dir)

        # Build aggregated data
        aggregated = build_aggregated_data(benchmarks)

        # Write per-run data.json files
        _write_per_run_data(output_dir, benchmarks)

        # Write output
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "benchmarks.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(aggregated, f, indent=2)

        print(f"Generated {output_file}")
        print(f"  Benchmarks: {aggregated['summary'].get('total_benchmarks', 0)}")
        print(f"  Skills: {aggregated['summary'].get('total_skills', 0)}")

        return True

    except Exception as e:
        print(f"Error generating dashboard data: {e}")
        return False


if __name__ == "__main__":
    import sys

    # Default paths
    results_dir = Path("tests/data-history")
    output_dir = Path("site/benchmarks")

    # Allow command line overrides
    if len(sys.argv) > 1:
        results_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])

    success = generate_dashboard_data(results_dir, output_dir)
    sys.exit(0 if success else 1)

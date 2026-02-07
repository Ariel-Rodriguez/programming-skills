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


def _parse_benchmark_id(benchmark_id: str) -> tuple[str | None, str | None, str | None]:
    """
    Parse benchmark_id in the format: provider-model-YYYYMMDD-HHMMSS

    Returns:
        (provider, model, timestamp) or (None, None, None) if not matched.
    """
    match = re.match(r'^(?P<provider>[^-]+)-(?P<model>.+)-(?P<timestamp>\d{8}-\d{6})$', benchmark_id)
    if not match:
        return None, None, None
    return match.group('provider'), match.group('model'), match.group('timestamp')


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


def _benchmark_id_from_path(file_path: Path) -> str:
    """
    Determine benchmark_id based on file path.
    """
    if file_path.name == "summary.json":
        return file_path.parent.name
    return file_path.stem


def process_benchmark_file(file_path: Path) -> dict | None:
    """
    Process a single benchmark JSON file and extract structured data.

    Args:
        file_path: Path to the benchmark JSON file

    Returns:
        Structured benchmark data dict or None if processing fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading {file_path}: {e}")
        return None

    benchmark_id = _benchmark_id_from_path(file_path)

    # Extract timestamp from summary or benchmark id
    timestamp = _normalize_timestamp(data.get('timestamp', ''))
    if not timestamp:
        _, _, parsed_timestamp = _parse_benchmark_id(benchmark_id)
        if parsed_timestamp:
            timestamp = _normalize_timestamp(parsed_timestamp)
    if not timestamp:
        match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})', file_path.stem)
        if match:
            timestamp = _normalize_timestamp(match.group(1))

    # Get provider and model from JSON data (primary source)
    results = data.get('results', [])

    provider = 'unknown'
    model = 'unknown'

    if results:
        model = results[0].get('model', 'unknown')

    parsed_provider, parsed_model, _ = _parse_benchmark_id(benchmark_id)
    if provider == 'unknown' and parsed_provider:
        provider = parsed_provider
    if (not model or model == 'unknown') and parsed_model:
        model = parsed_model

    if (not model or model == 'unknown'):
        model_match = re.search(r'benchmark-[^-]+-(.+)-\d{4}', benchmark_id)
        if model_match:
            model = model_match.group(1)

    if provider == 'unknown':
        if 'cloud' in str(model).lower():
            provider = 'ollama'
        elif 'ollama' in benchmark_id:
            provider = 'ollama'
        elif 'copilot' in benchmark_id:
            provider = 'copilot'
        elif 'gemini' in benchmark_id:
            provider = 'gemini'

    # Get results from data
    results = data.get('results', [])
    if not results:
        return None

    # Build skills list
    skills = []
    for result in results:
        judgment = result.get('judgment', {})

        # Get before/after code from test results
        test_results = result.get('results', [])
        before_code, after_code = extract_code_from_test_results(test_results, provider)

        # Determine improvement
        overall_better = judgment.get('overall_better', 'Equal')
        if overall_better == 'B':
            improvement = 'yes'
        elif overall_better == 'A':
            improvement = 'no'
        else:
            improvement = 'neutral'

        skill_data = {
            'skill_name': result.get('skill', 'unknown'),
            'provider': provider,
            'model': model,
            'timestamp': timestamp,
            'baseline_rating': normalize_rating(judgment.get('option_a_rating', '')),
            'skill_rating': normalize_rating(judgment.get('option_b_rating', '')),
            'improvement': improvement,
            'reasoning': extract_judgment_reasoning(judgment),
            'before_code': before_code,
            'after_code': after_code,
            'judgment': judgment
        }
        skills.append(skill_data)

    return {
        'benchmark_id': benchmark_id,
        'timestamp': timestamp,
        'provider': provider,
        'model': model,
        'skills': skills
    }


def collect_all_benchmarks(benchmarks_dir: Path) -> list[dict]:
    """
    Collect all benchmark data from a directory.

    Args:
        benchmarks_dir: Directory containing benchmark JSON files

    Returns:
        List of structured benchmark data
    """
    if not benchmarks_dir.exists():
        return []

    all_data = []

    # Look for summary.json files
    for summary_file in benchmarks_dir.glob('**/summary.json'):
        data = process_benchmark_file(summary_file)
        if data:
            all_data.append(data)

    # Also look for benchmark-*.json files
    for benchmark_file in benchmarks_dir.glob('**/benchmark-*.json'):
        data = process_benchmark_file(benchmark_file)
        if data:
            all_data.append(data)

    # Sort by timestamp (newest first)
    all_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    return all_data


def _write_per_run_data(benchmarks_dir: Path) -> None:
    """
    Write per-run data.json next to each summary.json file.
    """
    for summary_file in benchmarks_dir.glob('**/summary.json'):
        benchmark = process_benchmark_file(summary_file)
        if not benchmark:
            continue
        per_run = build_aggregated_data([benchmark])
        output_file = summary_file.parent / "data.json"
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


def generate_dashboard_data(benchmarks_dir: Path, output_file: Path) -> bool:
    """
    Main function: Generate dashboard data from benchmark files.

    Pure function - only reads from benchmarks_dir, writes to output_file
    and per-run data.json files next to summary.json.

    Args:
        benchmarks_dir: Directory containing benchmark JSON files
        output_file: Path to write aggregated data JSON

    Returns:
        True if successful, False otherwise
    """
    try:
        # Collect all benchmarks
        benchmarks = collect_all_benchmarks(benchmarks_dir)

        # Build aggregated data
        aggregated = build_aggregated_data(benchmarks)

        # Write per-run data.json files
        _write_per_run_data(benchmarks_dir)

        # Write output
        output_file.parent.mkdir(parents=True, exist_ok=True)
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
    benchmarks_dir = Path("docs/benchmarks")
    output_file = Path("docs/benchmarks/benchmarks.json")

    # Allow command line overrides
    if len(sys.argv) > 1:
        benchmarks_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])

    success = generate_dashboard_data(benchmarks_dir, output_file)
    sys.exit(0 if success else 1)

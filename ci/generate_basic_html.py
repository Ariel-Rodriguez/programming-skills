"""
Generate Basic HTML - Pure Function

Generates a Bootstrap-styled HTML page from benchmark data.
This is a pure function - no side effects.
"""

import json
from pathlib import Path
from typing import Any


def generate_html_page(data: dict) -> str:
    """
    Generate HTML page from benchmark data.

    Args:
        data: Aggregated benchmark data

    Returns:
        HTML string
    """
    summary = data.get('summary', {})
    benchmarks = data.get('benchmarks', [])
    unique_skills = data.get('unique_skills', [])
    provider_models = data.get('provider_models', [])

    # Build provider/model options
    provider_options = ""
    seen_providers = set()
    for prov, model in provider_models:
        if prov not in seen_providers:
            provider_options += f'<option value="{prov}">{prov.capitalize()}</option>'
            seen_providers.add(prov)

    # Build skill rows
    skill_rows = ""
    for benchmark in benchmarks:
        for skill in benchmark.get('skills', []):
            skill_name = skill.get('skill_name', 'unknown')
            provider = skill.get('provider', 'unknown')
            model = skill.get('model', 'unknown')
            baseline_rating = skill.get('baseline_rating', 'vague')
            skill_rating = skill.get('skill_rating', 'vague')
            improvement = skill.get('improvement', 'neutral')
            before_code = skill.get('before_code', '// No code generated')
            after_code = skill.get('after_code', '// No code generated')
            reasoning = skill.get('reasoning', 'No reasoning')

            # Get rating colors
            baseline_color = get_rating_color(baseline_rating)
            skill_color = get_rating_color(skill_rating)

            # Escape code for HTML
            before_code_escaped = escape_html(before_code)
            after_code_escaped = escape_html(after_code)

            # Format reasoning for HTML
            reasoning_formatted = format_reasoning(reasoning)

            skill_rows += f'''
            <tr>
                <td>{skill_name}</td>
                <td>{provider.capitalize()}</td>
                <td>{model}</td>
                <td><span class="badge bg-{baseline_color}">{baseline_rating}</span></td>
                <td><span class="badge bg-{skill_color}">{skill_rating}</span></td>
                <td><span class="badge bg-{get_improvement_color(improvement)}">{improvement.capitalize()}</span></td>
                <td><button class="btn btn-sm btn-primary" onclick="showDetails({json.dumps(skill)})">View</button></td>
            </tr>
            '''

    # Build unique skills filter options
    skills_filter = '<option value="">All Skills</option>'
    for skill_name in unique_skills:
        skills_filter += f'<option value="{skill_name}">{skill_name}</option>'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Programming Skills Benchmarks</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .code-container {{
            background-color: #f8f9fa;
            border-radius: 6px;
            padding: 10px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .rating-badge {{
            font-size: 0.9em;
            padding: 4px 8px;
        }}
        .judgment-box {{
            background-color: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 12px;
            margin-bottom: 16px;
        }}
        .code-comparison {{
            background-color: #f8f9fa;
            border-radius: 6px;
            padding: 16px;
            margin-top: 16px;
        }}
        .code-section {{
            margin-bottom: 16px;
        }}
        .code-section h7 {{
            color: #6c757d;
            margin-bottom: 8px;
        }}
        pre {{
            background-color: #fff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 12px;
            overflow-x: auto;
        }}
        #detailModal .modal-dialog {{
            max-width: 90%;
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <span class="navbar-brand">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
                Programming Skills Benchmarks
            </span>
            <button class="btn btn-sm btn-outline-light" onclick="refreshData()">Refresh</button>
        </div>
    </nav>

    <!-- Summary Cards -->
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Total Benchmarks</h5>
                        <h2 class="card-text">{summary.get('total_benchmarks', 0)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Skills Tested</h5>
                        <h2 class="card-text">{summary.get('total_skills', 0)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Improvements</h5>
                        <h2 class="card-text text-success">{summary.get('improvements', 0)}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Improvement Rate</h5>
                        <h2 class="card-text">{summary.get('improvement_rate', 0)}%</h2>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Filters -->
    <div class="container mt-4">
        <div class="row g-2 align-items-end">
            <div class="col-md-3">
                <label class="form-label fw-bold">Provider</label>
                <select class="form-select" id="filter-provider" onchange="filterTable()">
                    <option value="">All Providers</option>
                    {provider_options}
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label fw-bold">Model</label>
                <select class="form-select" id="filter-model" onchange="filterTable()">
                    <option value="">All Models</option>
                    {"".join(f'<option value="{prov} {mdl}">{prov.capitalize()} - {mdl}</option>' for prov, mdl in provider_models)}
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label fw-bold">Skill</label>
                <select class="form-select" id="filter-skill" onchange="filterTable()">
                    {skills_filter}
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label fw-bold">Improvement</label>
                <select class="form-select" id="filter-improvement" onchange="filterTable()">
                    <option value="">All</option>
                    <option value="yes">Improvement</option>
                    <option value="no">Regression</option>
                    <option value="neutral">Neutral</option>
                </select>
            </div>
        </div>
    </div>

    <!-- Skills Table -->
    <div class="container mt-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Benchmark Results</h5>
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-striped table-hover mb-0" id="skills-table">
                        <thead class="table-light">
                            <tr>
                                <th>Skill</th>
                                <th>Provider</th>
                                <th>Model</th>
                                <th>Before</th>
                                <th>After</th>
                                <th>Improvement</th>
                                <th>View Details</th>
                            </tr>
                        </thead>
                        <tbody id="skills-table-body">
                            {skill_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal for Details -->
    <div class="modal fade" id="detailModal" tabindex="-1">
        <div class="modal-dialog modal-xl modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="detailModalTitle">Skill Details</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="modal-content">
                        <!-- Populated by JS -->
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Custom JS -->
    <script>
        // Data loaded from external JSON
        let allData = {json.dumps(data, indent=2)};

        function getRatingColor(rating) {{
            const colors = {{
                'vague': 'secondary',
                'regular': 'warning',
                'good': 'primary',
                'outstanding': 'success'
            }};
            return colors[rating] || 'secondary';
        }}

        function getImprovementColor(improvement) {{
            const colors = {{
                'yes': 'success',
                'no': 'danger',
                'neutral': 'secondary'
            }};
            return colors[improvement] || 'secondary';
        }}

        function escapeHtml(text) {{
            if (!text) return '';
            return text
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }}

        function formatReasoning(reasoning) {{
            return reasoning.replace(/\\n/g, '<br>');
        }}

        function showDetails(skill) {{
            const modalTitle = document.getElementById('detailModalTitle');
            const modalContent = document.getElementById('modal-content');

            modalTitle.textContent = `Details: ${{
                skill.skill_name || 'Unknown Skill'
            }}`;

            const judgment = skill.judgment || {{
                'option_a_rating': 'vague',
                'option_b_rating': 'vague',
                'overall_better': 'Equal',
                'reasoning': 'No judgment available'
            }};

            const judgmentBox = `<div class="judgment-box">
                <h6>Judge Assessment</h6>
                <p><strong>Before (Baseline):</strong> ${{
                    judgment.option_a_rating || 'vague'
                }}</p>
                <p><strong>After (With Skill):</strong> ${{
                    judgment.option_b_rating || 'vague'
                }}</p>
                <p><strong>Overall Better:</strong> ${{
                    judgment.overall_better || 'Equal'
                }}</p>
                <hr>
                <p><strong>Reasoning:</strong></p>
                <div>${{
                    formatReasoning(skill.reasoning || 'No reasoning')
                }}</div>
            </div>`;

            const codeComparison = `<div class="code-comparison">
                <div class="row">
                    <div class="col-md-6">
                        <div class="code-section">
                            <h7>Before (Baseline)</h7>
                            <div class="code-container">
                                <pre><code>${{
                                    escapeHtml(skill.before_code || '// No code generated')
                                }}</code></pre>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="code-section">
                            <h7>After (With Skill)</h7>
                            <div class="code-container">
                                <pre><code>${{
                                    escapeHtml(skill.after_code || '// No code generated')
                                }}</code></pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;

            modalContent.innerHTML = judgmentBox + codeComparison;

            const modal = new bootstrap.Modal(document.getElementById('detailModal'));
            modal.show();
        }}

        function filterTable() {{
            const provider = document.getElementById('filter-provider').value.toLowerCase();
            const model = document.getElementById('filter-model').value.toLowerCase();
            const skill = document.getElementById('filter-skill').value.toLowerCase();
            const improvement = document.getElementById('filter-improvement').value.toLowerCase();

            const rows = document.querySelectorAll('#skills-table-body tr');
            let visibleCount = 0;

            rows.forEach(row => {{
                const cells = row.cells;
                const rowProvider = cells[1].textContent.toLowerCase();
                const rowModel = cells[2].textContent.toLowerCase();
                const rowSkill = cells[0].textContent.toLowerCase();
                const rowImprovement = cells[5].textContent.toLowerCase();

                const matchProvider = !provider || rowProvider.includes(provider);
                const matchModel = !model || rowModel.includes(model);
                const matchSkill = !skill || rowSkill.includes(skill);
                const matchImprovement = !improvement || rowImprovement.includes(improvement);

                if (matchProvider && matchModel && matchSkill && matchImprovement) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});

            console.log(`Showing ${{
                visibleCount
            }} skills`);
        }}

        function refreshData() {{
            // Reload the page to get fresh data
            window.location.reload();
        }}

        // Initial table render
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Benchmarks loaded:', allData.benchmarks.length, 'benchmarks');
            console.log('Total skills:', allData.summary.total_skills);
        }});
    </script>
</body>
</html>'''

    return html


def generate_basic_html(input_file: Path, output_file: Path) -> bool:
    """
    Main function: Generate HTML page from benchmark JSON.

    Pure function - only reads from input_file, writes to output_file.

    Args:
        input_file: Path to aggregated benchmark JSON
        output_file: Path to write HTML file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read input
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Generate HTML
        html = generate_html_page(data)

        # Write output
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"Generated {output_file}")
        return True

    except Exception as e:
        print(f"Error generating HTML: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys

    # Default paths
    input_file = Path("docs/benchmarks.json")
    output_file = Path("docs/index.html")

    # Allow command line overrides
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])

    success = generate_basic_html(input_file, output_file)
    sys.exit(0 if success else 1)

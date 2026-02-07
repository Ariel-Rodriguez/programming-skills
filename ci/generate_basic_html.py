"""
Generate Basic HTML - Pure Function

Generates a Bootstrap-styled HTML page from benchmark data.
This is a pure function - no side effects.
"""

from pathlib import Path


def generate_html_page(data_src: str, script_src: str) -> str:
    """
    Generate HTML page from benchmark data.

    Args:
        data_src: Relative path to benchmark JSON
        script_src: Relative path to app.js

    Returns:
        HTML string
    """
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Programming Skills Benchmarks</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
    <style>
        .code-container {{
            background-color: #f8f9fa;
            border-radius: 6px;
            padding: 10px;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #dee2e6;
        }}
        .code-container.expanded {{
            max-height: none;
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
<body data-benchmarks-src="{data_src}">
    <!-- Header -->
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <span class="navbar-brand">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
                Programming Skills Benchmarks
            </span>
            <button class="btn btn-sm btn-outline-light" onclick="refreshDashboard()">Refresh</button>
        </div>
    </nav>

    <!-- Summary Cards -->
    <div class="container mt-4">
        <div class="row" id="summary-cards">
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Total Benchmarks</h5>
                        <h2 class="card-text" id="summary-total-benchmarks">0</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Skills Tested</h5>
                        <h2 class="card-text" id="summary-total-skills">0</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Improvements</h5>
                        <h2 class="card-text text-success" id="summary-improvements">0</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Improvement Rate</h5>
                        <h2 class="card-text" id="summary-improvement-rate">0%</h2>
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
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label fw-bold">Model</label>
                <select class="form-select" id="filter-model" onchange="filterTable()">
                    <option value="">All Models</option>
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label fw-bold">Skill</label>
                <select class="form-select" id="filter-skill" onchange="filterTable()">
                    <option value="">All Skills</option>
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
                    <div class="judgment-box">
                        <h6>Judge Assessment</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Before (Baseline):</strong> <span id="modal-before-rating"></span></p>
                                <p><strong>After (With Skill):</strong> <span id="modal-after-rating"></span></p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Overall Better:</strong> <span id="modal-better"></span></p>
                                <p><strong>Judge Score:</strong> <span id="modal-score"></span>/100</p>
                            </div>
                        </div>
                        <hr>
                        <div><strong>Reasoning:</strong> <div id="modal-reasoning"></div></div>
                    </div>

                    <div class="code-comparison">
                        <h6>Code Comparison</h6>

                        <div class="code-section">
                            <h7>Before (Baseline) <small class="text-muted">Click to expand</small></h7>
                            <div class="code-container" id="modal-before-code">
                                <pre><code class="language-javascript" id="code-before"></code></pre>
                            </div>
                            <button class="btn btn-sm btn-outline-primary mt-2" onclick="toggleExpand('modal-before-code', this)">Expand</button>
                        </div>

                        <div class="code-section">
                            <h7>After (With Skill) <small class="text-muted">Click to expand</small></h7>
                            <div class="code-container" id="modal-after-code">
                                <pre><code class="language-javascript" id="code-after"></code></pre>
                            </div>
                            <button class="btn btn-sm btn-outline-primary mt-2" onclick="toggleExpand('modal-after-code', this)">Expand</button>
                        </div>
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
    <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.js"></script>
    <script src="{script_src}"></script>
</body>
</html>'''

    return html


def generate_basic_html(input_file: Path, output_file: Path, data_src: str = "benchmarks.json", script_src: str = "scripts/app.js") -> bool:
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
        # Generate HTML
        html = generate_html_page(data_src, script_src)

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
    input_file = Path("docs/benchmarks/benchmarks.json")
    output_file = Path("docs/benchmarks/index.html")

    # Allow command line overrides
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])

    success = generate_basic_html(input_file, output_file)
    sys.exit(0 if success else 1)

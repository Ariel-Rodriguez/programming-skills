# Benchmark Dashboard Page Specification

## Overview

This spec describes the HTML/CSS/JS structure for the benchmark dashboard page.

## Tech Stack (MVP)

- **HTML5**: Semantic structure
- **Bootstrap 5**: CSS framework for layout and components
- **Vanilla JavaScript**: No build step, pure client-side
- **Prism.js (CDN)**: For syntax highlighting in code blocks
- **Chart.js (CDN)**: For future time series charts
- **Diff Match Patch (CDN)**: For code comparison highlighting

## Directory Structure

```
docs/
└── benchmarks/
    ├── {benchmark_id}/                 # Each run gets its own folder
    │   ├── summary.json                # Full benchmark results
    │   ├── data.json                   # Extracted data for dashboard
    │   └── index.html                  # Individual page for this run
    ├── index.html                      # Main dashboard (aggregated)
    └── benchmarks.json                 # Aggregated data for JS
```

## Page Structure (index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Programming Skills Benchmarks</title>

  <!-- Bootstrap 5 CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

  <!-- Prism.js for syntax highlighting -->
  <link href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">

  <style>
    /* Custom styles */
    .code-container {
      background-color: #f8f9fa;
      border-radius: 6px;
      max-height: 400px;
      overflow-y: auto;
      border: 1px solid #dee2e6;
    }
    .code-comparison .code-section {
      margin-bottom: 16px;
    }
    .code-comparison h7 {
      color: #6c757d;
      font-weight: 600;
    }
    .judgment-box {
      background-color: #e7f3ff;
      border-left: 4px solid #2196F3;
      padding: 16px;
      margin-bottom: 20px;
      border-radius: 4px;
    }
    .expandable-content {
      display: none;
    }
    .expandable-content.expanded {
      display: block;
    }
  </style>
</head>
<body data-benchmarks-src="benchmarks.json">
  <!-- Header -->
  <nav class="navbar navbar-dark bg-dark">
    <div class="container">
      <span class="navbar-brand">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
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
      <!-- Populated by JS -->
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
                <th>Details</th>
              </tr>
            </thead>
            <tbody id="skills-table-body">
              <!-- Populated by JS -->
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
          <!-- Judgment Reasoning -->
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

          <!-- Code Comparison -->
          <div class="code-comparison">
            <h6>Code Comparison</h6>

            <div class="code-section">
              <h7>Before (Baseline) <small class="text-muted">Click to expand</small></h7>
              <div class="code-container" id="modal-before-code">
                <pre><code class="language-javascript" id="code-before"></code></pre>
              </div>
              <button class="btn btn-sm btn-outline-primary mt-2" onclick="toggleExpand('modal-before-code')">Expand</button>
            </div>

            <div class="code-section">
              <h7>After (With Skill) <small class="text-muted">Click to expand</small></h7>
              <div class="code-container" id="modal-after-code">
                <pre><code class="language-javascript" id="code-after"></code></pre>
              </div>
              <button class="btn btn-sm btn-outline-primary mt-2" onclick="toggleExpand('modal-after-code')">Expand</button>
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
  <!-- Prism.js -->
  <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.js"></script>
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <!-- Diff Match Patch -->
  <script src="https://cdn.jsdelivr.net/npm/diff-match-patch@1.0.5/index.min.js"></script>

  <!-- Custom JS -->
  <script src="scripts/app.js"></script>
</body>
</html>
```

## Data Loading (scripts/app.js)

```javascript
// Load aggregated data from data-benchmarks-src attribute
const src = document.body.dataset.benchmarksSrc || 'benchmarks.json';
fetch(src)
  .then(response => response.json())
  .then(data => {
    renderSummary(data.summary);
    renderTable(data.benchmarks);
    populateFilters(data);
  });
```

Per-run pages set `data-benchmarks-src="data.json"` on the `<body>` tag.

## Data Structure

### Aggregated Data Format
```json
{
  "benchmarks": [
    {
      "benchmark_id": "ollama-rnj-1-8b-cloud-2026-02-07T14-30-00",
      "timestamp": "2026-02-07T14:30:00",
      "provider": "ollama",
      "model": "rnj-1:8b-cloud",
      "skills": [
        {
          "skill_name": "ps-composition-over-coordination",
          "baseline_rating": "vague",
          "skill_rating": "outstanding",
          "improvement": "yes",
          "reasoning": "...\n\nJudgment: ...",
          "before_code": "full code...",
          "after_code": "full code..."
        }
      ]
    }
  ],
  "summary": {
    "total_benchmarks": 5,
    "total_skills": 60,
    "improvements": 45,
    "regressions": 3,
    "neutral": 12
  }
}
```

## Key Features

### 1. Filter Table
- Filter by provider (ollama, copilot, gemini)
- Filter by model name
- Filter by skill name
- Filter by improvement status

### 2. Expandable Code Display
- Code blocks show partial content by default (300 lines max)
- Expand button to show full code
- Syntax highlighting with Prism.js

### 3. Modal Details
- Judgment reasoning with clear formatting
- Side-by-side code comparison
- Rating badges (vague/regular/good/outstanding)

### 4. History Preservation
- Each benchmark run stored in `docs/benchmarks/{timestamp}/`
- `index.html` aggregates all benchmarks
- Previous results never overwritten

## Implementation Tasks

1. **Fix provider/model extraction** - Parse from JSON correctly
2. **Add expandable code blocks** - Default to truncated, show expand button
3. **Debug filters** - Ensure filterTable() works correctly
4. **Fix data structure** - Use timestamped directories for each run
5. **Update publish workflow** - Save to versioned folders

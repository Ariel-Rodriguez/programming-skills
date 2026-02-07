# Benchmark Dashboard Page Specification

## Overview

This spec describes the HTML/CSS/JS structure for the benchmark dashboard page.

## Tech Stack (MVP)

- **HTML5**: Semantic structure
- **Bootstrap 5**: CSS framework for layout and components
- **Vanilla JavaScript**: No build step, pure client-side
- **Chart.js (CDN)**: For future time series charts
- **Diff Match Patch (CDN)**: For code comparison highlighting

## Page Structure

```html
<!DOCTYPE html>
<html>
<head>
  <!-- Bootstrap 5 CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <style>
    /* Custom styles for code diff highlighting */
    .code-diff-add { background-color: #d4edda; }
    .code-diff-remove { background-color: #f8d7da; }
    .code-line-numbers { background-color: #f8f9fa; }
  </style>
</head>
<body>
  <!-- Header -->
  <nav class="navbar navbar-dark bg-dark">
    <div class="container">
      <span class="navbar-brand">Programming Skills Benchmarks</span>
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
            <h2 class="card-text" id="total-benchmarks">0</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Skills Tested</h5>
            <h2 class="card-text" id="total-skills">0</h2>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Last Updated</h5>
            <p class="card-text" id="last-updated">-</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Filters -->
  <div class="container mt-4">
    <div class="row">
      <div class="col">
        <div class="input-group">
          <span class="input-group-text">Filter by:</span>
          <select class="form-select" id="filter-provider">
            <option value="">All Providers</option>
          </select>
          <select class="form-select" id="filter-model">
            <option value="">All Models</option>
          </select>
        </div>
      </div>
    </div>
  </div>

  <!-- Skills Table -->
  <div class="container mt-4">
    <table class="table table-striped table-hover" id="skills-table">
      <thead>
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
        <!-- Rows populated by JS -->
      </tbody>
    </table>
  </div>

  <!-- Modal for Details -->
  <div class="modal fade" id="detailModal" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="detailModalTitle">Skill Details</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <!-- Judgment Reasoning -->
          <div class="mb-3">
            <h6>Judge Reasoning</h6>
            <div class="alert alert-info" id="detail-reasoning"></div>
          </div>

          <!-- Code Comparison -->
          <div>
            <h6>Code Comparison</h6>
            <div class="row">
              <div class="col">
                <h7>Before (Baseline)</h7>
                <pre class="bg-light p-2 rounded" id="detail-before-code"></pre>
              </div>
              <div class="col">
                <h7>After (With Skill)</h7>
                <pre class="bg-light p-2 rounded" id="detail-after-code"></pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Bootstrap JS -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <!-- Diff Match Patch -->
  <script src="https://cdn.jsdelivr.net/npm/diff-match-patch@1.0.5/index.min.js"></script>
  <!-- Custom JS -->
  <script src="scripts/app.js"></script>
</body>
</html>
```

## Data Loading

```javascript
// Load aggregated data from docs/benchmarks.json
fetch('benchmarks.json')
  .then(response => response.json())
  .then(data => {
    renderSummary(data);
    renderTable(data);
  });
```

## Table Row Structure

```javascript
function renderTableRow(skill) {
  return `
    <tr>
      <td>${skill.name}</td>
      <td>${skill.provider}</td>
      <td>${skill.model}</td>
      <td><span class="badge bg-${ratingColor(skill.baseline_rating)}">${skill.baseline_rating}</span></td>
      <td><span class="badge bg-${ratingColor(skill.skill_rating)}">${skill.skill_rating}</span></td>
      <td>
        ${skill.improvement === 'yes'
          ? '<span class="badge bg-success">Yes</span>'
          : '<span class="badge bg-secondary">No</span>'}
      </td>
      <td><button class="btn btn-sm btn-primary" onclick="showDetails(${JSON.stringify(skill)})">View</button></td>
    </tr>
  `;
}
```

## Code Diff Highlighting (Future Enhancement)

```javascript
function highlightCodeDiff(before, after) {
  const dmp = new diff_match_patch();
  const diffs = dmp.diff_main(before, after);
  dmp.diff_cleanupSemantic(diffs);

  return diffs.map(([op, text]) => {
    if (op === 1) return `<span class="code-diff-add">${text}</span>`;  // Add
    if (op === -1) return `<span class="code-diff-remove">${text}</span>`;  // Remove
    return text;
  }).join('');
}
```

## Chart.js Integration (Future)

```javascript
function renderTimeSeriesChart(data) {
  const ctx = document.getElementById('improvementChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.timestamps,
      datasets: [{
        label: 'Average Improvement',
        data: data.improvements,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }]
    }
  });
}
```

## Future Enhancements

1. **Time Series Charts**: Show improvement over time
2. **Provider Comparison**: Bar chart comparing providers
3. **Skill Heatmap**: Visual representation of improvement by skill
4. **Export Function**: Download results as CSV
5. **Version Comparison**: Compare any two benchmark runs

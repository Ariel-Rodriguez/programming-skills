# Benchmark Dashboard Workflow Specification

## Overview

This spec describes the end-to-end workflow for running manual benchmarks and publishing results to GitHub Pages.

## Trigger

Manual trigger via GitHub Actions workflow dispatch with inputs:
- **provider**: Choice dropdown (ollama, copilot, gemini)
- **model**: Free text input (e.g., qwen-coder-next:cloud)

## Data Flow

```
Manual GitHub Actions Trigger
  inputs: provider (choice), model (string)
    ↓
Run evaluation for provider/model → tests/results/summary.json
    ↓
Copy to tests/results/summary-{benchmark_id}.json
    ↓
Generate dashboard data (pure function)
    ↓
Copy src/pages/benchmarks → output root (default: site/benchmarks)
    ↓
Write benchmarks.json + data/{benchmark_id}/data.json
    ↓
Push output root to benchmark-history orphan branch
    ↓
GitHub Pages serves benchmark-history branch
```

## Folder Structure

```
src/
└── pages/
    └── benchmarks/               # Source dashboard UI
        ├── index.html
        ├── app.js
        └── data/                 # Optional dev data

site/
└── benchmarks/                   # Generated output (auto-created)
    ├── index.html                # Copied from src/pages/benchmarks
    ├── app.js                    # Copied from src/pages/benchmarks
    ├── benchmarks.json           # Aggregated data for JS
    └── data/
        └── {benchmark_id}/
            └── data.json          # Per-run data for dashboard
```

## Files

### `.github/workflows/benchmark-dashboard.yml`

GitHub Actions workflow that:
1. Accepts manual trigger with provider/model inputs
2. Runs evaluation using existing evaluator.py
3. Downloads and consolidates results
4. Pushes to orphan branch

### `ci/publish_benchmarks.py`

Main orchestration script:
- Coordinates all steps
- Handles errors gracefully
- Writes to site/benchmarks/

### `ci/orphan_branch_manager.py`

Handles orphan branch operations:
- Creates/updates benchmark-history branch
- Manages git operations
- Ensures clean commits

### `ci/generate_dashboard_data.py`

Pure function that:
- Reads evaluation JSON files
- Extracts structured data for dashboard
- Returns consistent format

### Static HTML/JS Source

- Static HTML/JS is sourced from `src/pages/benchmarks/`.
- Publish step copies it into the output root before writing JSON data.

## Output Format

```json
{
  "benchmark_id": "ollama-qwen-coder-next-cloud-2026-02-07T12-00-00",
  "timestamp": "2026-02-07T12:00:00Z",
  "provider": "ollama",
  "model": "qwen-coder-next:cloud",
  "skills": [
    {
      "name": "ps-composition-over-coordination",
      "baseline_rating": "good",
      "skill_rating": "outstanding",
      "improvement": "yes",
      "reasoning": "...",
      "before_code": "original code...",
      "after_code": "improved code..."
    }
  ]
}
```

## HTML Structure

```
Bootstrap 5 + minimal JS
├── Header (title, timestamp, provider/model info)
├── Summary cards (quick stats)
├── Skills table (filterable)
│   └── Click to expand for details
│       ├── Judgment reasoning
│       ├── Before/After code comparison
└── Footer (refresh button, source info)
```

## Orphan Branch: benchmark-history

- Single branch for all benchmark data
- Contains: site/benchmarks/ (flat root for GitHub Pages)
- GitHub Pages serves this branch directly

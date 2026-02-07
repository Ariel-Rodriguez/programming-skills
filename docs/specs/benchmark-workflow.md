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
Run evaluation for provider/model → artifact/
    ↓
Download artifacts
    ↓
Generate dashboard data (pure function)
    ↓
Save to docs/benchmarks/{timestamp}.json
    ↓
Push docs/ to benchmark-history orphan branch
    ↓
Generate basic index.html
    ↓
Commit & push index.html to orphan branch
    ↓
GitHub Pages serves benchmark-history branch
```

## Folder Structure

```
docs/
├── specs/
│   ├── benchmark-workflow.md     # This file
│   └── benchmark-page.md         # Page design spec (separate spec)
├── benchmarks/                   # Generated data (auto-created)
│   ├── {timestamp}.json          # Individual benchmark results
│   └── index.html                # Dashboard page
└── benchmarks.json               # Aggregated data for quick access
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
- Writes to docs/benchmarks/

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

### `ci/generate_basic_html.py`

Pure function that:
- Takes structured data
- Generates Bootstrap-styled HTML
- Outputs index.html

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
- Contains: docs/benchmarks/ + docs/benchmarks.json
- GitHub Pages serves this branch directly

# Benchmarks Dashboard (Source)

This folder is the **source of truth** for the benchmark dashboard UI.

## What lives here
- `index.html`: static template for the dashboard
- `app.js`: client-side rendering and filtering logic
- `data/`: optional local data for development

## How it is published
Publishing **copies this folder** into the build output root (default: `site/benchmarks`) and then writes:
- `benchmarks.json` (aggregated)
- `data/<benchmark_id>/data.json` (per-run)

The orphan branch is created from that output root, so GitHub Pages serves `index.html` at `/`.

## Notes
- Do **not** edit generated files in `site/benchmarks/`.
- All dashboard changes should be made here.

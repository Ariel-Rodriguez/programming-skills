# Generate Benchmark Data

This guide shows the current end-to-end flow for generating benchmark history and publishing the dashboard.

## Prerequisites

- Run from the repo root.
- Codex CLI or Copilot CLI installed (if using those providers).
- `site/` output is generated locally and **not** committed to `main`.

## 1) Run an Evaluation

Run a full benchmark run and write results into `tests/data-history/`.

### Codex

```bash
uv run --project tests tests/evaluator.py \
  --provider codex \
  --model gpt-5.1-codex-mini \
  --judge --verbose \
  --all
```

### Copilot

```bash
uv run --project tests tests/evaluator.py \
  --provider copilot \
  --model sonnet \
  --judge --verbose \
  --all
```

### Ollama

```bash
uv run --project tests tests/evaluator.py \
  --provider ollama \
  --model llama3.2:latest \
  --judge --verbose \
  --all
```

Results are written to:

```
tests/data-history/
  summary-<provider>-<model>-<timestamp>.json
  <skill>/<model>-<timestamp>.json
```

## 2) Generate the Site Output

This copies `src/pages/benchmarks/` into the output root and generates JSON data.

```bash
python3 ci/publish_benchmarks.py \
  --no-benchmark \
  --output-dir site/benchmarks
```

Output is created at:

```
site/benchmarks/
  index.html
  app.js
  benchmarks.json
  data/<benchmark_id>/data.json
```

## 3) Publish the Orphan Branch

```bash
git checkout benchmark-history
git rm -rf .
cp -R site/benchmarks/. .
git add .
git commit -m "Publish benchmark dashboard"
git push origin benchmark-history
git checkout main
```

## Notes

- The dashboard aggregates all runs in `tests/data-history/`.
- The orphan branch is a **flat root** for GitHub Pages.
- If you need to debug outputs, inspect `site/benchmarks/benchmarks.json`.

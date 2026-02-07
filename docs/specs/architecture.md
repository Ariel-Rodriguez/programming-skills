# Architecture

## Design Principles

- **Simplicity**: Skills are defined once with clear principles and examples.
- **Single Source of Truth**: The `skills/` directory contains all skill definitions and their associated benchmark scenarios.
- **Language Independence**: Principles apply to any programming language, with pseudocode for illustrations.
- **Severity-Based Enforcement**: Skills are categorized by impact (BLOCK, WARN, SUGGEST).
- **Reproducible Benchmarks**: Benchmark history is versioned under `tests/data-history/`.

## Directory Structure

```
programming-skills/
├── skills/                      # Skill definitions
│   ├── ps-functional-core-imperative-shell/
│   │   ├── SKILL.md             # Principle & Documentation
│   │   ├── test.json            # Benchmark scenarios & expectations
│   │   └── example_case.js       # (Optional) External input files
│   └── ...
├── tests/                       # Benchmarking suite
│   ├── evaluator.py             # Main evaluation engine
│   ├── data-history/            # Versioned benchmark history
│   │   ├── summary-<provider>-<model>-<timestamp>.json
│   │   └── <skill>/<model>-<timestamp>.json
│   └── config.yaml              # Benchmarking configuration
├── src/
│   └── pages/
│       └── benchmarks/          # Dashboard source (index.html + app.js)
├── site/
│   └── benchmarks/              # Generated output (not committed)
├── ci/                          # CI scripts and publishing
└── docs/                        # Documentation
    ├── specs/
    │   ├── architecture.md
    │   ├── benchmark-workflow.md
    │   └── benchmark-page.md
    ├── contributing.md
    ├── install-instructions.md
    └── generate-benchmark.md
```

## Skill Format

Each skill is a directory containing:

1. **SKILL.md**: YAML frontmatter with `name`, `description`, and `severity`.
2. **test.json**: Benchmark test cases for the evaluator.
3. **Support Files**: Optional source files referenced by `test.json`.

### Severity Levels

- **BLOCK**: Architectural violations requiring immediate refactoring.
- **WARN**: Significant issues that should be flagged with justification.
- **SUGGEST**: Optional improvements that enhance quality.

## Benchmarking Flow

1. **Evaluator** runs baseline + skill prompt per test case.
2. **Summary** written to `tests/data-history/summary-<provider>-<model>-<timestamp>.json`.
3. **Per-skill history** written to `tests/data-history/<skill>/<model>-<timestamp>.json`.
4. **Dashboard build** reads history and produces:
   - `site/benchmarks/benchmarks.json`
   - `site/benchmarks/data/<benchmark_id>/data.json`
5. **Publish** copies `site/benchmarks/` into the orphan branch root for GitHub Pages.

## Platform Support

Skills are filesystem-based and should be placed where your AI tool reads skills from. See:

```
https://agentskills.io/integrate-skills
https://agentskills.io/llms.txt
```

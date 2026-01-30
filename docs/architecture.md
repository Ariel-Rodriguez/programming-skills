# Architecture

## Design Principles

- **Simplicity**: Skills are defined once with clear principles and examples.
- **Single Source of Truth**: The `skills/` directory contains all skill definitions and their associated benchmark scenarios.
- **Language Independence**: Principles are documented in a way that applies to any programming language, typically using pseudocode for illustrations.
- **Severity-Based Enforcement**: Skills are categorized by impact (BLOCK, WARN, SUGGEST) to guide AI agents on how to handle violations.

## Directory Structure

```text
basic-programming-skills/
├── skills/                      # Skill definitions
│   ├── ps-functional-core-imperative-shell/
│   │   ├── SKILL.md            # Principle & Documentation
│   │   ├── test.json           # Benchmark scenarios & expectations
│   │   └── example_case.js      # (Optional) External input files
│   └── ...
├── tests/                       # Benchmarking suite
│   ├── evaluator.py            # Main evaluation engine
│   └── config.yaml             # Benchmarking configuration
├── docs/                        # Project documentation
│   ├── architecture.md
│   ├── contributing.md
│   └── ai-prompt-wrapper.md
└── README.md
```

## Skill Format (v2.2.0)

Each skill is a directory containing:

1.  **SKILL.md**: A markdown file with YAML frontmatter containing `name`, `description`, and `severity`.
2.  **test.json**: A machine-readable file containing benchmark test cases.
3.  **Support Files**: Optional source code files referenced by `test.json` for complex scenarios.

### Severity Levels

- **BLOCK**: Architectural or structural violations that must stop code generation and require immediate refactoring.
- **WARN**: Significant design issues that should be flagged and explained, but may be bypassed with justification.
- **SUGGEST**: Optional improvements or refinements that enhance code quality without being critical.

## Automated Benchmarking

The project includes a robust benchmarking system to verify that AI models can correctly apply the defined skills.

### Evaluator Engine

The `tests/evaluator.py` script:
- Automatically discovers skills and their corresponding `test.json` files.
- Executes tests against models using the Ollama REST API.
- Supports dual-pass evaluation: a baseline run (without skill context) and a skill run (with skill context).
- Calculates the improvement delta and pass rates.

### Test Schema

Tests in `test.json` support:
- **`includes`**: Strings that must all be present in the model's response.
- **`excludes`**: Strings that must not appear in the response.
- **`regex`**: Regular expression patterns for advanced verification.
- **`min_length` / `max_length`**: Character count constraints.
- **External Inputs**: Inputs can reference a filename in the same directory, which the evaluator will load dynamically.

## Platform Support

The skills are designed to be copied directly into AI agent environments:
- **Cursor**: Copy `skills/` to `.cursor/skills/`.
- **Antigravity**: Copy `skills/` to `.agent/skills/`.

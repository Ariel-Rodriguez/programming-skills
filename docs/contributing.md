# Contributing to Basic Programming Skills

Thank you for your interest in improving AI agent skills for better code quality!

## Current Version: v2.2.0

This repository is organized around self-documenting skills that include automated benchmark tests to ensure reliability across different AI models.

## Repository Structure

```text
basic-programming-skills/
├── skills/              # All skill definitions
│   ├── ps-skill-name/
│   │   ├── SKILL.md    # Documentation & Examples
│   │   └── test.json   # Benchmark scenarios
├── tests/               # Benchmarking engine
└── docs/                # Documentation
```

## Adding a New Skill

### 1. Create the Skill Folder

```bash
cd skills
mkdir ps-your-skill-name  # Use lowercase-with-hyphens
cd ps-your-skill-name
```

### 2. Create SKILL.md

Every skill needs a `SKILL.md` with YAML frontmatter:

```markdown
---
name: ps-your-skill-name
description: Short description for AI context discovery.
severity: BLOCK | WARN | SUGGEST
---

# Your Skill Name

## Principle
What core rule does this skill enforce?

## When to Use
List specific scenarios or code smells.

## Instructions
✅ **Do:** Clear guidelines.
❌ **Avoid:** Common anti-patterns.

## Examples (Pseudocode)
Use language-agnostic pseudocode for principles.
```

### 3. Create test.json

Benchmark scenarios ensure the skill works. Tests use the following schema:

```json
[
  {
    "name": "scenario_name",
    "input": "Code snippet or external_file.js",
    "expected": {
      "includes": ["term_must_exist"],
      "excludes": ["forbidden_pattern"],
      "regex": ["pattern\\d+"],
      "min_length": 50
    }
  }
]
```

## Testing & Benchmarking

Before submitting, verify your skill with the built-in evaluator:

```bash
# Run benchmark for your specific skill
uv run python tests/evaluator.py --skill ps-your-skill-name --verbose
```

### Verification Checklist
- [ ] Correct `severity` assigned in `SKILL.md`.
- [ ] At least 2 test scenarios in `test.json`.
- [ ] Pass rate > 50% for the "With Skill" run.
- [ ] No grammar or spelling errors in documentation.

## Submit Pull Request

1. Fork the repository.
2. Add your skill folder.
3. Update `README.md` and `CHANGELOG.md`.
4. Submit PR with a clear description of the new principle.

## License

By contributing, you agree your contributions will be licensed under the MIT License.

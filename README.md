# Programming Skills

Language-agnostic AI agent skills that enforce fundamental programming principles. This repository provides specific, granular instructions that enable AI coding assistants to produce significantly higher-quality code that adheres to robust engineering standards.

Adopting these skills measurably changes the output of AI models, shifting them from generating merely functional code to producing architecturally sound solutions.

## Table of Contents

- [Installation](#installation)
- [How it Works](#how-it-works)
- [Validation & Testing](#validation--testing)
- [Evaluation Results](#evaluation-results)
- [Documentation](#documentation)
- [License](#license)

## Installation

Select your platform for specific setup instructions:

- [Cursor](docs/install/cursor.md)
- [Antigravity](docs/install/antigravity.md)
- [GitHub Copilot](docs/install/copilot.md)
- [Claude](docs/install/claude.md)

## How it Works

The core of this repository is the `skills/` directory. Each skill is encapsulated in its own subdirectory following the `ps-<name>` convention (e.g., `ps-composition-over-coordination`).

We use this granular structure because:
1.  **Focus**: It allows the AI to load only the relevant context for a specific task, avoiding context window pollution.
2.  **Modularity**: Skills can be improved, versioned, and tested independently.
3.  **Composability**: Users can select the specific combination of principles they want to enforce for their project.

## Validation & Testing

Every skill is validated against a rigorous testing suite found in the `tests/` directory.

- **Automated Judging**: We use an LLM-as-a-Judge approach. The system compares the output of a "Baseline" model (without the skill) against a "Skill" model (with the skill loaded).
- **Semantics over Syntax**: The test does not just look for passing unit tests; it analyzes the *logic* and *structure* of the code.
- **Evidence-Based**: The judge identifies the specific lines of code that demonstrate adherence to or violation of the principle.

[Read our Case Study on Judge Fairness](docs/judge-fairness-case-study.md) to see how the system fairly evaluates architectural quality, even when it means failing the Skill model.

## Evaluation Results

Processed 24 evaluation(s).

| Test Name | Model | Baseline | With Skill | Cases Pass | Winner |
|-----------|-------|----------|------------|------------|--------|
| [results-ollama-devstral-small-2--24b-cloud-ps-composition-over-coordination](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329534502) | devstral-small-2:24b-cloud | good | good | ✅ 2/2 | N/A |
| [results-ollama-devstral-small-2--24b-cloud-ps-error-handling-design](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329534340) | devstral-small-2:24b-cloud | regular | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-devstral-small-2--24b-cloud-ps-explicit-boundaries-adapters](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329535854) | devstral-small-2:24b-cloud | good | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-devstral-small-2--24b-cloud-ps-explicit-ownership-lifecycle](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329535894) | devstral-small-2:24b-cloud | good | good | ✅ 2/2 | With Skill |
| [results-ollama-devstral-small-2--24b-cloud-ps-explicit-state-invariants](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329537422) | devstral-small-2:24b-cloud | good | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-devstral-small-2--24b-cloud-ps-functional-core-imperative-shell](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329537046) | devstral-small-2:24b-cloud | regular | good | ✅ 2/2 | With Skill |
| [results-ollama-devstral-small-2--24b-cloud-ps-illegal-states-unrepresentable](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329538523) | devstral-small-2:24b-cloud | good | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-devstral-small-2--24b-cloud-ps-local-reasoning](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329538780) | devstral-small-2:24b-cloud | good | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-devstral-small-2--24b-cloud-ps-minimize-mutation](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329540068) | devstral-small-2:24b-cloud | good | good | ✅ 2/2 | N/A |
| [results-ollama-devstral-small-2--24b-cloud-ps-naming-as-design](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329540040) | devstral-small-2:24b-cloud | regular | good | ✅ 2/2 | With Skill |
| [results-ollama-devstral-small-2--24b-cloud-ps-policy-mechanism-separation](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329541792) | devstral-small-2:24b-cloud | good | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-devstral-small-2--24b-cloud-ps-single-direction-data-flow](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329541535) | devstral-small-2:24b-cloud | regular | good | ✅ 2/2 | With Skill |
| [results-ollama-rnj-1--8b-cloud-ps-composition-over-coordination](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329524580) | rnj-1:8b-cloud | outstanding | good | ❌ 2/2 | Baseline |
| [results-ollama-rnj-1--8b-cloud-ps-error-handling-design](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329524126) | rnj-1:8b-cloud | vague | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-rnj-1--8b-cloud-ps-explicit-boundaries-adapters](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329526125) | rnj-1:8b-cloud | regular | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-rnj-1--8b-cloud-ps-explicit-ownership-lifecycle](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329526263) | rnj-1:8b-cloud | good | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-rnj-1--8b-cloud-ps-explicit-state-invariants](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329528479) | rnj-1:8b-cloud | regular | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-rnj-1--8b-cloud-ps-functional-core-imperative-shell](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329527817) | rnj-1:8b-cloud | regular | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-rnj-1--8b-cloud-ps-illegal-states-unrepresentable](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329529527) | rnj-1:8b-cloud | outstanding | outstanding | ✅ 2/2 | N/A |
| [results-ollama-rnj-1--8b-cloud-ps-local-reasoning](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329529241) | rnj-1:8b-cloud | vague | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-rnj-1--8b-cloud-ps-minimize-mutation](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329531124) | rnj-1:8b-cloud | regular | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-rnj-1--8b-cloud-ps-naming-as-design](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329531393) | rnj-1:8b-cloud | vague | good | ✅ 2/2 | With Skill |
| [results-ollama-rnj-1--8b-cloud-ps-policy-mechanism-separation](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329532599) | rnj-1:8b-cloud | regular | outstanding | ✅ 2/2 | With Skill |
| [results-ollama-rnj-1--8b-cloud-ps-single-direction-data-flow](https://github.com/Ariel-Rodriguez/programming-skills/actions/runs/21547621647/artifacts/5329532551) | rnj-1:8b-cloud | vague | good | ✅ 2/2 | With Skill |

## Documentation

- [Architecture](docs/architecture.md) - Repository design & structure
- [Contributing](docs/contributing.md) - How to add/modify skills & benchmarks
- [AI Prompt Wrapper](docs/ai-prompt-wrapper.md) - Configure your AI assistant
- [Changelog](CHANGELOG.md) - Version history & skill changes

## License

MIT License - see [LICENSE](LICENSE)

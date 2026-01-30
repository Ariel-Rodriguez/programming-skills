# Programming Skills

**Version:** 1.0.0

Language-agnostic AI agent skills that enforce fundamental programming principles across Cursor, Antigravity, GitHub Copilot, and other AI coding assistants.

## Quick Start

```bash
# Linux/macOS - Cursor/Antigravity
curl -L https://github.com/Ariel-Rodriguez/programming-skills/releases/latest/download/cursor-antigravity.zip -o skills.zip && unzip skills.zip -d .cursor/skills && rm skills.zip

# Windows (PowerShell) - Cursor/Antigravity
Invoke-WebRequest -Uri "https://github.com/Ariel-Rodriguez/programming-skills/releases/latest/download/cursor-antigravity.zip" -OutFile "skills.zip"; Expand-Archive -Path "skills.zip" -DestinationPath ".cursor\skills" -Force; Remove-Item "skills.zip"
```

[Manual installation & more options →](docs/contributing.md#adding-a-new-skill)

## Skills Overview

| # | Skill | Category | Purpose |
|---|-------|----------|---------|
| 1 | [Functional Core / Imperative Shell](skills/functional-core-imperative-shell/) | Core | Separate pure logic from effects |
| 2 | [Explicit State Invariants](skills/explicit-state-invariants/) | Core | Design state with clear invariants |
| 3 | [Single Direction Data Flow](skills/single-direction-data-flow/) | Core | Unidirectional data flow |
| 4 | [Explicit Boundaries & Adapters](skills/explicit-boundaries-adapters/) | Design | Isolate frameworks |
| 5 | [Local Reasoning](skills/local-reasoning/) | Design | Understandable locally |
| 6 | [Naming as Design](skills/naming-as-design/) | Design | Intent-revealing names |
| 7 | [Error Handling Design](skills/error-handling-design/) | Design | Model errors explicitly |
| 8 | [Policy/Mechanism Separation](skills/policy-mechanism-separation/) | Design | Separate what from how |
| 9 | [Explicit Ownership Lifecycle](skills/explicit-ownership-lifecycle/) | Design | Clear resource ownership |
| 10 | [Minimize Mutation](skills/minimize-mutation/) | Design | Control mutation |
| 11 | [Composition Over Coordination](skills/composition-over-coordination/) | Refinement | Compose, don't orchestrate |
| 12 | [Illegal States Unrepresentable](skills/illegal-states-unrepresentable/) | Refinement | Prevent misuse structurally |

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | Repository design & structure (v1.0.0) |
| [Contributing](docs/contributing.md) | How to add/modify skills + PR format |
| [AI Prompt Wrapper](docs/ai-prompt-wrapper.md) | Configure your AI assistant |
| [Future Design](docs/future-skills-design.md) | Roadmap for v2.0.0 |
| [Changelog](CHANGELOG.md) | Version history & skill changes |
| [Benchmarks](benchmarks/) | Evaluate AI models against skills |

## Supported Platforms

- ✅ **Cursor** 2.4+
- ✅ **Antigravity**
- ✅ **GitHub Copilot**
- ✅ Any Agent Skills compatible tool

## Contributing

```bash
# Add a new skill
mkdir skills/my-new-skill
# Create SKILL.md with pseudocode examples
# Submit PR
```

See [Contributing Guide](docs/contributing.md) for details.

## License

MIT License - see [LICENSE](LICENSE)

## Credits

Principles derived from *Programming: Principles and Practice Using C++* and *A Tour of C++* by Bjarne Stroustrup, adapted for AI-assisted development.

---

**Repository:** https://github.com/Ariel-Rodriguez/programming-skills

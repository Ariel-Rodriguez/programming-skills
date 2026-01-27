# Architecture

## Design Principles

**Simplicity**: Skills defined once with clear pseudocode examples, no language-specific implementations needed.

**Single Source of Truth**: `skills/` contains all skill definitions with inline pseudocode examples.

**No Build Process**: Skills are ready to use as-is, no compilation or transformation required.

## Directory Structure

```
basic-programming-skills/
├── skills/                      # Skill definitions
│   ├── functional-core-imperative-shell/
│   │   └── SKILL.md            # Complete skill with pseudocode
│   └── ...
│
├── ci/                          # Release automation
│   └── release.sh
│
├── .github/workflows/           # CI/CD pipelines
│
└── docs/                        # Documentation
    └── architecture.md         # This file
```

## Skill Format

Each `SKILL.md` contains:
1. YAML frontmatter with name and description
2. Principle and explanation
3. When to apply
4. How to implement
5. **Inline pseudocode examples** (language-agnostic)
6. Testing strategy (using pseudocode)
7. Review checklist

## Why This Design?

### ✅ Advantages

1. **Simplicity**: No build process, no JSON merging, no placeholders
2. **Clarity**: Examples are directly in the skill file
3. **Language Independence**: Pseudocode works for all languages
4. **Maintainability**: One file per skill, easy to update
5. **Ready to Use**: Copy skills/ folder directly into your project

### 🔄 Usage

**Using skills:**
```bash
1. Clone repository
2. Copy skills/ folder to .cursor/skills/ or .agent/skills/
3. Done - no build step needed
```

**Adding a new skill:**
```bash
1. Create skills/new-skill/SKILL.md
2. Write skill content with pseudocode examples
3. Done - immediately usable
```

## Platform Support

### Cursor & Antigravity
- Use SKILL.md format directly
- Copy skills/ folder to `.cursor/skills/` or `.agent/skills/`
- YAML frontmatter + markdown body

### Copilot
- Uses `.github/copilot/instructions.md`
- Different format from Agent Skills standard
- Maintained separately in copilot/ folder

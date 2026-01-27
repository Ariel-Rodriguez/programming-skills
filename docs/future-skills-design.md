# Future Skills Design (v2.0.0)

This file documents a proposed future format for programming skills that includes severity mapping and enforcement levels.

> **Note:** This is a design document for future versions. Current version (v1.0.0) uses simple pseudocode-based SKILL.md files without this structure.

## Version History

- **v1.0.0** (Current): Skills use inline pseudocode examples. No severity levels enforced by tooling.
- **v2.0.0** (Proposed): Skills include machine-readable severity mapping and enforcement rules.

## Proposed Format: Severity-Based Enforcement

### Enforcement Levels

- **BLOCK**: Code generation must stop. Refactoring required before proceeding.
- **WARN**: Flag the violation, explain the issue, and suggest corrections.
- **SUGGEST**: Optional improvement. Mention only when clearly beneficial.

### Severity Assignments (Proposed v2.0.0)

```yaml
ai_code_culture:
  version: "2.0.0"
  severity:
    # Core structural skills - BLOCKING
    functional-core-imperative-shell: BLOCK
    explicit-state-invariants: BLOCK
    single-direction-data-flow: BLOCK
    
    # Design discipline skills - WARNING
    explicit-boundaries-adapters: WARN
    local-reasoning: WARN
    naming-as-design: WARN
    error-handling-design: WARN
    policy-mechanism-separation: WARN
    explicit-ownership-lifecycle: WARN
    minimize-mutation: WARN
    
    # Refinement skills - SUGGESTION
    composition-over-coordination: SUGGEST
    illegal-states-unrepresentable: SUGGEST
```

## Enforcement Rules (v2.0.0 Proposal)

### BLOCK Skills (1-3)

If any BLOCK skill is violated:
1. **Stop** code generation immediately
2. **Explain** the specific violation with examples
3. **Refactor** the code before continuing
4. **Verify** the fix addresses the root issue

These skills prevent architectural debt and reactive chaos.

### WARN Skills (4-10)

When violated:
1. **Flag** the issue clearly
2. **Explain** why it matters (invariants, ownership, flow)
3. **Suggest** specific refactoring approach
4. **Continue** if user explicitly approves the tradeoff

### SUGGEST Skills (11-12)

When applicable:
1. **Note** the improvement opportunity
2. **Explain** the benefit briefly
3. **Offer** to implement if user is interested
4. **Don't block** or repeat if declined

## Response Template (v2.0.0)

When a skill is violated, AI agents would use this format:

```
Skill violated: <SKILL_NAME>
Severity: <BLOCK | WARN | SUGGEST>

Issue:
<Concise explanation of what's wrong>

Why it matters:
<Connection to code quality, maintainability, or correctness>

Required change:
<Specific refactoring approach>

[BLOCK only: Proceeding only after resolution]
```

## Project-Level Overrides (v2.0.0)

Projects could override defaults via `.ai-skills-config.yaml`:

```yaml
version: "2.0.0"
overrides:
  functional-core-imperative-shell: WARN  # Relax to warning
  illegal-states-unrepresentable: BLOCK   # Elevate to blocking
```

## Migration Path

To migrate from v1.0.0 to v2.0.0:

1. Add `severity` field to each SKILL.md frontmatter
2. Create enforcement tooling (linters, IDE extensions)
3. Add `.ai-skills-config.yaml` support
4. Update CI/CD to validate severity compliance

## Current State (v1.0.0)

The current version focuses on clarity and simplicity:
- Skills use pseudocode for language independence
- No formal severity enforcement
- AI agents interpret skills based on content, not metadata
- Users manually configure their AI assistants

This approach prioritizes:
- **Ease of contribution**: Anyone can add a skill
- **Readability**: Skills are just markdown
- **Flexibility**: No rigid structure to follow

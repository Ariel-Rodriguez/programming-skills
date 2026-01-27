# Contributing to Basic Programming Skills

Thank you for your interest in improving AI agent skills for better code quality!

## Current Version: v1.0.0

This repository is currently at version **1.0.0**, which uses a simple, pseudocode-based format for maximum clarity and language independence. See [future-skills-design.md](future-skills-design.md) for proposed v2.0.0 enhancements.

## Repository Structure

```
basic-programming-skills/
├── skills/              # All skill definitions (SKILL.md files)
├── ci/                  # Release automation scripts
├── .github/workflows/   # CI/CD pipelines
└── docs/                # Documentation
    ├── architecture.md
    ├── contributing.md (this file)
    ├── ai-prompt-wrapper.md
    └── future-skills-design.md
```

## Adding a New Skill

### 1. Create the Skill Folder

```bash
cd skills
mkdir your-skill-name  # Use lowercase-with-hyphens
cd your-skill-name
```

### 2. Create SKILL.md

Every skill needs a `SKILL.md` with YAML frontmatter:

```markdown
---
name: your-skill-name
description: Short description that helps AI decide when to use this skill. Mention keywords and use cases.
---

# Your Skill Name

## Principle

What is the core principle this skill enforces?

## When to Use

- List specific scenarios
- When code smells like X
- During Y type of work

## Instructions

### Core guidelines

✅ **Do:**
- Clear requirement

❌ **Avoid:**
- Clear anti-pattern

## Examples

### ✅ Good: Description

\```
FUNCTION goodExample():
    // Pseudocode showing correct pattern
    RETURN result
\```

*Explanation of why this is good.*

### ❌ Bad: Description

\```
FUNCTION badExample():
    // Pseudocode showing anti-pattern
    RETURN result
\```

*Explanation of why this is problematic.*

## Testing Strategy

\```
TEST "description":
    // Arrange - Set up test data
    input = createTestData()
    expected = createExpectedResult()
    
    // Act - Execute function
    result = function(input)
    
    // Assert - Verify result
    ASSERT result EQUALS expected
\```

## AI Review Checklist

- [ ] Specific question to verify compliance
- [ ] Another verification question

**If [condition] → [Action] (WARN/SUGGEST)**

## Related Patterns

- Links to related skills

## References

- Links to foundational articles/talks
```

### 3. Use Pseudocode, Not Real Code

**v1.0.0 uses language-agnostic pseudocode:**

✅ **Good:**
```
FUNCTION calculateTotal(items):
    subtotal = sum(items.map(item => item.price))
    RETURN subtotal
```

❌ **Bad:**
```javascript
const calculateTotal = (items) => {
  return items.reduce((sum, item) => sum + item.price, 0);
};
```

**Why:** Pseudocode works for all programming languages. Real code examples may be added in v2.0.0.

### 4. Follow AAA Pattern for Tests

**All test examples must follow Arrange-Act-Assert pattern:**

```
TEST "description":
    // Arrange - Set up test data and conditions
    input = createTestData()
    expected = createExpectedResult()
    
    // Act - Execute the function being tested
    result = functionUnderTest(input)
    
    // Assert - Verify the result
    ASSERT result EQUALS expected
```

**Why:** AAA pattern makes tests clear, consistent, and easy to understand. It explicitly separates setup, execution, and verification.

### 4. Test the Skill

1. Copy the skill folder to `.cursor/skills/` or `.agent/skills/`
2. Open your AI assistant
3. Test by asking it to review code that violates the skill
4. Verify it catches violations and suggests fixes

### 5. Submit Pull Request

1. Fork the repository
2. Add your skill to `skills/`
3. Update `README.md` to list the new skill
4. Update `CHANGELOG.md` under `[Unreleased]` section
5. Submit PR using the format below

**PR Title Format:**

```
<type>: <description>

Types:
- feat: New skill added
- improve: Existing skill improved
- fix: Bug fix or correction
- docs: Documentation only changes
- chore: Build, CI/CD, or tooling changes

Examples:
- feat: add retry-with-backoff skill
- improve: clarify functional-core examples
- fix: correct typo in naming-as-design
- docs: update installation instructions
```

**PR Description Template:**

```markdown
## Changes
- Brief description of what changed

## Skill Impact
- Which skills were added/modified?
- Why was this change needed?

## Testing
- How did you test this change?

## Checklist
- [ ] Updated CHANGELOG.md
- [ ] Updated README.md (if new skill)
- [ ] Tested locally with AI assistant
- [ ] Followed pseudocode format (no language-specific code)
```

## Skill Quality Guidelines

### Descriptions

✅ **Good:**
> "Enforces separation of pure logic from side effects. Use when reviewing code that mixes business logic with IO, framework calls, or state mutations."

❌ **Bad:**
> "A skill about functions and separation."

**Why:** AI needs keywords and context to decide when to apply the skill.

### Examples

- Include both ✅ GOOD and ❌ BAD examples
- Use realistic pseudocode, not toy examples
- Show the fix, not just the problem
- Cover edge cases

### Language

- Be prescriptive: "Must", "Must not", "Should"
- Use active voice
- Keep it scannable with headers
- Include checklists for AI to verify

### Scope

- One skill = one principle
- Don't try to cover everything
- Deep, not broad
- Focus on "why", not just "how"

## Updating Existing Skills

### Small Improvements

- Fix typos, improve examples, add clarifications
- Submit PR directly

### Major Changes

- Open an issue first to discuss
- Explain the problem with current version
- Propose specific improvements

## Testing

We don't have automated tests yet (contributions welcome!), but you can test manually:

1. Install the skill in your local setup
2. Write code that violates the skill
3. Ask your AI assistant to review it
4. Verify it catches the violation
5. Verify the suggested fix is correct

## Style Guide

- Use Markdown format
- Use pseudocode for all examples (language-agnostic)
- Use emoji sparingly (✅ ❌ are fine for examples)
- Keep tone professional but friendly
- Structure: Principle → When to Apply → How to Implement → Examples → Testing

## Release Process

Maintainers follow this workflow:

1. **Merge PR** - Review and merge contributor PRs
2. **Update CHANGELOG** - Move `[Unreleased]` items to new version
3. **Tag Release** - Create git tag (e.g., `v1.1.0`)
4. **Auto-Release** - GitHub Actions generates `.zip` files
5. **Publish** - Release notes auto-generated from merged PRs

**Versioning:**
- **Major (2.0.0)**: Breaking format changes
- **Minor (1.1.0)**: New skills added
- **Patch (1.0.1)**: Fixes and improvements

## Questions?

- Open an issue with the `question` label
- Check [future-skills-design.md](future-skills-design.md) for roadmap

## License

By contributing, you agree your contributions will be licensed under the MIT License.

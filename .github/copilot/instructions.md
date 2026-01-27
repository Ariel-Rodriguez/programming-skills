# Copilot Instructions for basic-programming-skills Repository

## Communication Style

- **Minimal responses**: When a task is complete, respond with minimal confirmation like "done" or "done [brief description]"
- **No summaries**: Don't generate summaries of changes unless explicitly requested
- **No extra files**: Don't create planning files, notes, or tracking documents in the repository
- **Action-focused**: Execute tasks directly without lengthy explanations unless asked

## Repository Structure

This is a **skills collection repository** with the following structure:

```
basic-programming-skills/
├── skills/              # programming skills (SKILL.md files)
├── ci/                  # Release automation scripts
├── .github/workflows/   # CI/CD pipelines
└── docs/                # Documentation
```

## Code Principles

### Skills Format (v1.0.0)

- Use **pseudocode only** - no language-specific code examples
- Follow **AAA pattern** for all test examples (Arrange-Act-Assert)
- Keep examples clear and language-agnostic
- Structure: Principle → When to Use → Instructions → Examples → Testing

### Documentation

- README.md is a **reference index** - keep it short
- Detailed content belongs in `docs/` folder
- Don't duplicate documentation across files
- Use tables and diagrams (mermaid) for clarity

### Scripts

- All shell commands in `ci/` folder - no inline scripts in workflows
- Shell scripts must have LF line endings (enforced by .gitattributes)
- Make scripts executable: `chmod +x`

## Version Management

- **v1.0.0** format: Simple pseudocode-based skills
- Track changes in CHANGELOG.md
- Only document skills changes, not infrastructure changes
- Follow semantic versioning: Major.Minor.Patch

## PR and Commit Format

**PR Title Format:**
```
<type>: <description>

Types:
- feat: New skill added
- improve: Existing skill improved
- fix: Bug fix or correction
- docs: Documentation only
- chore: Build, CI/CD, tooling
```

## File Handling

- Don't create temporary/planning markdown files
- Update CHANGELOG.md for skill changes only
- Keep .gitignore minimal and relevant
- Use .gitattributes for line ending consistency

## When Working on Skills

1. **Adding new skill**: Create `skills/skill-name/SKILL.md`
2. **Update required**: README.md (table), CHANGELOG.md (if skill change)
3. **Test format**: Always use AAA pattern with comments
4. **Examples**: Good (✅) and Bad (❌) with explanations

## CI/CD

- Release on git tags: `v*`
- Generate two artifacts: `cursor-antigravity.zip`, `copilot.zip`
- Auto-generate release notes from merged PRs
- Artifacts retention: 1 day (only needed during workflow)

## Don't

- ❌ Create `plan.md` or tracking files
- ❌ Write lengthy summaries after completing tasks
- ❌ Add language-specific code examples to skills
- ❌ Duplicate content between README and docs/
- ❌ Inline shell commands in workflow YAML
- ❌ Update CHANGELOG for non-skill changes

## Do

- ✅ Respond with "done [brief note]" when task complete
- ✅ Use pseudocode for all examples
- ✅ Follow AAA pattern for tests
- ✅ Keep scripts in ci/ folder
- ✅ Update CHANGELOG for skill additions/changes
- ✅ Keep README as a reference index

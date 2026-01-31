# Installing on GitHub Copilot

## Configuration

GitHub Copilot (Enterprise) allows for repository-specific instructions.

1. Create or edit `.github/copilot/instructions.md` in your repository.
2. Add the core principles defined in the [AI Prompt Wrapper](../ai-prompt-wrapper.md).
3. (Optional) Append the full text of specific critical skills if you want strict enforcement on those topics.

## Example `instructions.md`

```markdown
You are an AI assistant giving programming advice.

When generating code, you must adhere to the following principles:
- **Functional Core / Imperative Shell**: Isolate pure logic.
- **Explicit State Invariants**: Document state validity.
... [Add specific skill instructions here]
```

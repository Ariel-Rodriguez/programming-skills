# Installing on Cursor

## Automatic Installation (Linux/macOS)

Run this command in your project root to download the standard skills to `.cursor/skills`:

```bash
curl -L https://github.com/Ariel-Rodriguez/programming-skills/releases/latest/download/cursor-antigravity.zip -o skills.zip && unzip skills.zip -d .cursor/skills && rm skills.zip
```

## Manual Installation

1. Create a `.cursor/skills` directory in your project root.
2. Copy the desired skill folders (e.g., `ps-composition-over-coordination`) from this repository into `.cursor/skills`.
3. Configure your `.cursorrules` to reference these skills.

See [AI Prompt Wrapper](../ai-prompt-wrapper.md) for configuration details.

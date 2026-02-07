# Skills Integration Guide

This repository organizes skills under the `skills/` directory. Each skill lives in its own folder and includes a `SKILL.md` file.

## Documentation Index

Fetch the complete documentation index at:

```
https://agentskills.io/llms.txt
```

Use this file to discover all available pages before exploring further.

## Integrate Skills Into Your Agent

Follow the integration guide here:

```
https://agentskills.io/integrate-skills
```

This guide explains how to:

1. Discover skills in configured directories
2. Load metadata at startup
3. Match tasks to relevant skills
4. Activate skills by loading full instructions
5. Execute scripts and access bundled assets as needed

---

Notes:

- Skills are filesystem-based: your agent should read `skills/*/SKILL.md`.
- Keep metadata concise; only load full skill instructions when needed.

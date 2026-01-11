---
allowed-tools: Bash(python3:*)
argument-hint: [planning|architecture|review] [codex|gemini|claude|off]
description: Set which provider handles a category implicitly
---

## Update routing target

- !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_config.py set-target $1 $2`

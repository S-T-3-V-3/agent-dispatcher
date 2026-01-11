---
allowed-tools: Bash(python3:*)
argument-hint: [extra context]
description: Ask the configured provider for architecture guidance
---

## Provider architecture output

- !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_exec.py --mode explicit --category architecture --prompt "$ARGUMENTS"`

## Your task

Use the provider output above as primary guidance. Summarize it clearly and answer the user.

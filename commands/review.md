---
allowed-tools: Bash(python3:*)
argument-hint: [extra context]
description: Ask the configured provider for review guidance
---

## Provider review output

- !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_exec.py --mode explicit --category review --prompt "$ARGUMENTS"`

## Your task

Use the provider output above as primary guidance. Summarize it clearly and answer the user.

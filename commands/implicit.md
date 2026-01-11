---
allowed-tools: Bash(python3:*)
argument-hint: [on|off]
description: Enable or disable implicit AI routing
---

## Toggle implicit routing

- !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_config.py set-implicit $1`

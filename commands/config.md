---
allowed-tools: Bash(python3:*)
description: Configure roles and providers
---

## Configuration

- Show current setup:
  - !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_cli.py summary`

- List roles:
  - !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_cli.py role list`

- Add a role (kebab-case):
  - !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_cli.py role add ui-dev --description "UI development focus"`

- Assign a provider to a role:
  - !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_cli.py role set-provider ui-dev codex`

- Disable a role:
  - !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_cli.py role disable ui-dev`

- Add a provider:
  - !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_cli.py provider add codex codex --model gpt-5.2-codex`
  - !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_cli.py provider add gemini gemini --model gemini-1.5-pro`
  - !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_cli.py provider add mycli command --command "mycli --prompt '{prompt}'"`

- Auth help:
  - !`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_cli.py auth-help`

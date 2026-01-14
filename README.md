# Agent Dispatcher Plugin

Configure AI roles and providers for Claude Code.

## What this plugin does

- Stores role and provider settings in `.claude/settings.json` under `agentDispatcher`.
- Stores role and provider settings in `.claude/settings.json` under `agentDispatcher`.
- Provides `setup` and `settings` commands for project configuration and management.
- Statusline is optional and shows enabled roles/providers when enabled.

## Install for local testing

```bash
claude --plugin-dir /home/codex/claude-marketplace/agent-dispatcher
```

## Configuration

Run:

```
/agent-dispatcher:setup
```

This command helps with first-time project configuration, such as enabling the statusline.

For ongoing management, run:

```
/agent-dispatcher:settings
```

This command allows you to view providers, roles, and toggle the statusline.

## Statusline format

Enabled roles are shown as:

```
Planning [Claude] | Architect [Codex] | Review [Gemini]
```

Disabled roles are omitted.

## Roles (default)

- planning
- architect
- review
- qa

Each role can be enabled/disabled and assigned to a provider. Role names must be kebab-case.

## Providers

- `claude` (always available)
- `codex`
- `gemini`
- custom command providers

## Auth options

- Codex: `codex login`, `codex login --device-auth`, or `printenv OPENAI_API_KEY | codex login --with-api-key`.
- Gemini: Google OAuth login via `gemini`, API key via `GEMINI_API_KEY`, or Vertex AI via `GOOGLE_API_KEY` + `GOOGLE_GENAI_USE_VERTEXAI=true`.

## Slash commands

- `/agent-dispatcher:setup` - first-time project configuration
- `/agent-dispatcher:settings` - manage providers, roles, and statusline

## Statusline toggle

Enable or disable per project:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/statusline/statusline_toggle.js" enable
node "${CLAUDE_PLUGIN_ROOT}/scripts/statusline/statusline_toggle.js" disable
```

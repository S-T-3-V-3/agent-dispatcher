# Agent Dispatcher Plugin

Configure AI roles and providers for Claude Code.

## What this plugin does

- Stores role and provider settings in `.claude/settings.json` under `agentDispatcher`.
- Provides a single configuration command that shows a fast menu.
- Statusline is optional and shows enabled roles/providers when enabled.

## Install for local testing

```bash
claude --plugin-dir /home/codex/claude-marketplace/agent-dispatcher
```

## Configuration

Run:

```
/agent-dispatcher:config
```

The command runs an interactive menu. It can also be used for first-time setup.

Menu files:

- `menu/main.md`
- `menu/help.md`
- `menu/roles.md`
- `menu/providers.md`
- `menu/settings.md`

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

- `/agent-dispatcher:config` - show the interactive menu

## Statusline toggle

Enable or disable per project:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/statusline/statusline_toggle.js" enable
node "${CLAUDE_PLUGIN_ROOT}/scripts/statusline/statusline_toggle.js" disable
```

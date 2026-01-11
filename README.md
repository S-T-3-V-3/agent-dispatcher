# AI Architect Plugin

Routes planning, architecture, and review work through configurable AI CLIs and injects their output into Claude Code.

## What this plugin does

- Adds a `UserPromptSubmit` hook that can implicitly route prompts to a provider.
- Stores routing settings in `.claude/settings.json` under `aiArchitect`.

## Install for local testing

```bash
claude --plugin-dir /home/codex/claude-marketplace/ai-architect
```

## First-time setup

Run:

```
/cc-distribution:config
```

This creates or updates `.claude/settings.json` with defaults and prints a summary.

## Routing settings

Stored in `.claude/settings.json`:

```json
{
  "aiArchitect": {
    "implicit": true,
    "targets": {
      "planning": "codex",
      "architecture": "codex",
      "review": "codex"
    },
    "providers": {
      "codex": {
        "kind": "codex",
        "model": "gpt-5.2-codex",
        "implicit": {
          "sandbox": "read-only",
          "approval": "never"
        },
        "explicit": {
          "sandbox": "workspace-write",
          "approval": "never"
        }
      },
      "gemini": {
        "kind": "gemini",
        "model": "gemini-1.5-pro",
        "implicit": {
          "sandbox": true,
          "approval_mode": "default"
        },
        "explicit": {
          "sandbox": false,
          "approval_mode": "auto_edit"
        }
      }
    }
  }
}
```

### Categories

- **Planning**: roadmaps, milestones, scope, requirements, sequencing.
- **Architecture**: system design, components, data models, infra, stack choices.
- **Review**: code review, audits, risks, refactor feedback.

### Targets

- `codex`: run Codex CLI and inject output.
- `gemini`: run Gemini CLI and inject output.
- `claude`: skip external provider and let Claude respond normally.
- `off`: skip external provider and ignore the category.

### Implicit routing

When `implicit` is `true`, the plugin uses a `UserPromptSubmit` hook to detect category keywords and, if the target is `codex` or `gemini`, runs that provider automatically. The result is injected as context for Claude to summarize.

## Slash commands

- `/cc-distribution:config` - interactive configuration and provider registration

## Notes

- Codex auth options: `codex login`, `codex login --device-auth`, or `printenv OPENAI_API_KEY | codex login --with-api-key`.
- Gemini auth options (from gemini-cli README): Google OAuth login via `gemini`, API key via `GEMINI_API_KEY`, or Vertex AI via `GOOGLE_API_KEY` + `GOOGLE_GENAI_USE_VERTEXAI=true`.
- For Codex, `implicit.sandbox` accepts `read-only`, `workspace-write`, or `danger-full-access`.
- For Gemini, `implicit.sandbox` is a boolean that maps to `--sandbox`, and `approval_mode` maps to `--approval-mode`.
- Rename the plugin by changing the `name` field in `.claude-plugin/plugin.json` if you want a shorter slash command prefix.

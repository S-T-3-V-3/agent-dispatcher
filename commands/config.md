---
description: Configure roles, providers, and project statusline
---

This command is an interactive setup and configuration flow. It is safe to run in a brand new project or to adjust an existing setup.

Use `AskUserQuestion` to show an interactive menu (do not render a numbered list). Offer these choices:
- Help
- Providers
- Roles
- Settings
- Exit

Then:
- If the user picks Help, render `${CLAUDE_PLUGIN_ROOT}/menu/help.md` verbatim.
- If the user picks Providers, render `${CLAUDE_PLUGIN_ROOT}/menu/providers.md` verbatim.
- If the user picks Roles, render `${CLAUDE_PLUGIN_ROOT}/menu/roles.md` verbatim.
- If the user picks Settings, render `${CLAUDE_PLUGIN_ROOT}/menu/settings.md` verbatim.
- If the user picks Exit, end the command.

First-time setup:
- Ask (via `AskUserQuestion`) whether this is a first-time setup for the project.
- If yes, ask whether to enable the statusline for this project.
- If the user agrees, run:

node "${CLAUDE_PLUGIN_ROOT}/scripts/statusline/statusline_toggle.js" enable

If the user wants to disable the statusline later, run:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/statusline/statusline_toggle.js" disable
```

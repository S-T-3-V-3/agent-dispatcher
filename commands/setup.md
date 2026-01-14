---
description: First-time setup for the project
---

# Setup

This command will help you configure the Agent Dispatcher for this project.

### Project Status

Use `AskUserQuestion` to ask: "Is this a first-time setup for this project?"
- Yes. This is a new project that hasn't been configured yet.
- No. This project has already been set up.

If the user picks "Yes":
    ### Statusline
    Use `AskUserQuestion` to ask: "Would you like to enable the statusline for this project? It will show the current role and provider in the footer."
    - Yes. Enable the statusline.
    - No. Keep it disabled.

    If the user picks "Yes":
        ```bash
        node "${CLAUDE_PLUGIN_ROOT}/scripts/statusline/statusline_toggle.js" enable
        ```
    Else:
        ```bash
        node "${CLAUDE_PLUGIN_ROOT}/scripts/statusline/statusline_toggle.js" disable
        ```
Else:
    The project is already set up. You can use `/agent-dispatcher:settings` to adjust your configuration.

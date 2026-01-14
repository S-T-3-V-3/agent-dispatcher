---
description: Manage plugin settings
---

# Settings

Manage your Agent Dispatcher configuration.

Use `AskUserQuestion` to ask: "What would you like to manage?"
- Providers. View information about configured AI providers.
- Roles. View information about configured AI roles.
- Statusline. Enable or disable the project statusline.
- Exit. Close settings.

### Choice: Providers
If the user picks "Providers":
    ### Providers
    The following providers are supported:
    - **claude**: The default Claude model.
    - **codex**: High-performance coding model.
    - **gemini**: Multimodal reasoning model.

    You can configure them in `.claude/settings.json` under `agentDispatcher.providers`.

    [Back to Settings]

### Choice: Roles
If the user picks "Roles":
    ### Roles
    Roles allow you to define specific behaviors and provider assignments.
    - Role names should be kebab-case (e.g., `code-reviewer`).
    - Each role can have a specific provider.
    - Enabled roles appear in the statusline.

    You can configure them in `.claude/settings.json` under `agentDispatcher.roles`.

    [Back to Settings]

### Choice: Statusline
If the user picks "Statusline":
    ### Statusline
    The statusline displays the currently active role and provider at the bottom of the Claude interface.

    Use `AskUserQuestion` to ask: "Would you like to enable or disable the statusline for this project?"
    - Enable. Show the statusline.
    - Disable. Hide the statusline.

    If the user picks "Enable":
        ```bash
        node "${CLAUDE_PLUGIN_ROOT}/scripts/statusline/statusline_toggle.js" enable
        ```
    Else:
        ```bash
        node "${CLAUDE_PLUGIN_ROOT}/scripts/statusline/statusline_toggle.js" disable
        ```

    [Back to Settings]

### Choice: Exit
If the user picks "Exit":
    Settings closed.

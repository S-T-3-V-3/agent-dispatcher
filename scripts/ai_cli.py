#!/usr/bin/env python3
import argparse
from pathlib import Path

from ai_lib import load_config, project_root, save_config, summarize_config, validate_role_name


def _exit_with(message: str, code: int = 2) -> int:
    print(message)
    return code



def _require_role(config: dict, role: str) -> dict | None:
    roles = config.get("roles", {})
    if role not in roles:
        return None
    return roles[role]


def _require_provider(config: dict, provider: str) -> dict | None:
    providers = config.get("providers", {})
    if provider not in providers:
        return None
    return providers[provider]


def _list_roles(config: dict) -> None:
    print(summarize_config(config))


def _add_role(config: dict, name: str, description: str | None) -> int:
    if not validate_role_name(name):
        return _exit_with("Role name must be kebab-case (lowercase letters, numbers, hyphens).")
    roles = config.setdefault("roles", {})
    if name in roles:
        return _exit_with("Role already exists.")
    roles[name] = {
        "enabled": True,
        "provider": "claude",
        "description": description or "",
    }
    return 0


def _remove_role(config: dict, name: str) -> int:
    roles = config.get("roles", {})
    if name not in roles:
        return _exit_with("Role not found.")
    roles.pop(name)
    return 0


def _rename_role(config: dict, old: str, new: str) -> int:
    if not validate_role_name(new):
        return _exit_with("New role name must be kebab-case.")
    roles = config.get("roles", {})
    if old not in roles:
        return _exit_with("Role not found.")
    if new in roles:
        return _exit_with("New role name already exists.")
    roles[new] = roles.pop(old)
    return 0


def _set_role_enabled(config: dict, name: str, enabled: bool) -> int:
    role_cfg = _require_role(config, name)
    if not role_cfg:
        return _exit_with("Role not found.")
    role_cfg["enabled"] = enabled
    return 0


def _set_role_provider(config: dict, name: str, provider: str) -> int:
    role_cfg = _require_role(config, name)
    if not role_cfg:
        return _exit_with("Role not found.")
    if not _require_provider(config, provider):
        return _exit_with("Provider not found.")
    role_cfg["provider"] = provider
    return 0


def _set_role_description(config: dict, name: str, description: str) -> int:
    role_cfg = _require_role(config, name)
    if not role_cfg:
        return _exit_with("Role not found.")
    role_cfg["description"] = description
    return 0


def _add_provider(config: dict, name: str, kind: str, model: str | None, command: str | None) -> int:
    providers = config.setdefault("providers", {})
    if name in providers:
        return _exit_with("Provider already exists.")
    if kind == "command" and not command:
        return _exit_with("Custom provider requires --command.")
    providers[name] = {
        "kind": kind,
    }
    if model:
        providers[name]["model"] = model
    if command:
        providers[name]["command"] = command
    return 0


def _edit_provider(config: dict, name: str, model: str | None, command: str | None) -> int:
    provider = _require_provider(config, name)
    if not provider:
        return _exit_with("Provider not found.")
    if provider.get("kind") == "claude":
        return _exit_with("Claude provider cannot be modified.")
    if model is not None:
        provider["model"] = model
    if command is not None:
        provider["command"] = command
    return 0


def _remove_provider(config: dict, name: str) -> int:
    if name == "claude":
        return _exit_with("Claude provider cannot be removed.")
    providers = config.get("providers", {})
    if name not in providers:
        return _exit_with("Provider not found.")
    roles = config.get("roles", {})
    for role, role_cfg in roles.items():
        if role_cfg.get("provider") == name:
            return _exit_with(f"Provider is assigned to role '{role}'. Reassign roles before removing.")
    providers.pop(name)
    return 0


def _print_auth_help() -> None:
    print("Codex auth options:")
    print("- Interactive login: codex login")
    print("- Device auth: codex login --device-auth")
    print("- API key: printenv OPENAI_API_KEY | codex login --with-api-key")
    print("")
    print("Gemini auth options (from gemini-cli README):")
    print("- Login with Google (OAuth): run 'gemini' and choose Login with Google")
    print("- Gemini API key: export GEMINI_API_KEY=... then run 'gemini'")
    print("- Vertex AI: export GOOGLE_API_KEY=... and GOOGLE_GENAI_USE_VERTEXAI=true")


def _menu_path(name: str) -> Path:
    return Path(__file__).resolve().parent.parent / "menu" / f"{name}.md"


def _print_menu_file(name: str) -> None:
    path = _menu_path(name)
    try:
        text = path.read_text(encoding="utf-8").rstrip()
    except OSError:
        text = f"== {name.title()} ==\n(missing menu template)\n=========="
    print(text)


def _print_roles_list(config: dict) -> None:
    roles = config.get("roles", {})
    if not roles:
        print("1. (no roles configured)")
        return
    for idx, (role, role_cfg) in enumerate(sorted(roles.items()), start=1):
        enabled = "on" if role_cfg.get("enabled", True) else "off"
        provider = role_cfg.get("provider", "claude")
        desc = role_cfg.get("description", "")
        suffix = f" - {desc}" if desc else ""
        print(f\"{idx}. {role} [{enabled}] ({provider}){suffix}\")


def _print_providers_list(config: dict) -> None:
    providers = config.get("providers", {})
    if not providers:
        print("1. (no providers configured)")
        return
    for idx, (name, provider) in enumerate(sorted(providers.items()), start=1):
        kind = provider.get("kind", "custom")
        model = provider.get("model")
        command = provider.get("command")
        extras = []
        if model:
            extras.append(f\"model={model}\")
        if command:
            extras.append(f\"command={command}\")
        extra_text = f\"; {', '.join(extras)}\" if extras else \"\"
        print(f\"{idx}. {name} ({kind}{extra_text})\")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage AI routing settings")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("summary", help="Show current routing configuration")
    sub.add_parser("auth-help", help="Show authentication guidance for providers")
    menu = sub.add_parser("menu", help="Show a fast menu")
    menu.add_argument("section", choices=("main", "help", "roles", "providers", "settings"))

    role = sub.add_parser("role", help="Manage roles")
    role_sub = role.add_subparsers(dest="role_cmd", required=True)
    role_sub.add_parser("list")

    role_add = role_sub.add_parser("add")
    role_add.add_argument("name")
    role_add.add_argument("--description", default="")

    role_remove = role_sub.add_parser("remove")
    role_remove.add_argument("name")

    role_rename = role_sub.add_parser("rename")
    role_rename.add_argument("old")
    role_rename.add_argument("new")

    role_enable = role_sub.add_parser("enable")
    role_enable.add_argument("name")

    role_disable = role_sub.add_parser("disable")
    role_disable.add_argument("name")

    role_provider = role_sub.add_parser("set-provider")
    role_provider.add_argument("name")
    role_provider.add_argument("provider")

    role_desc = role_sub.add_parser("set-description")
    role_desc.add_argument("name")
    role_desc.add_argument("description")

    provider = sub.add_parser("provider", help="Manage providers")
    provider_sub = provider.add_subparsers(dest="provider_cmd", required=True)
    provider_sub.add_parser("list")

    provider_add = provider_sub.add_parser("add")
    provider_add.add_argument("name")
    provider_add.add_argument("kind", choices=("codex", "gemini", "command"))
    provider_add.add_argument("--model")
    provider_add.add_argument("--command")

    provider_edit = provider_sub.add_parser("edit")
    provider_edit.add_argument("name")
    provider_edit.add_argument("--model")
    provider_edit.add_argument("--command")

    provider_remove = provider_sub.add_parser("remove")
    provider_remove.add_argument("name")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = project_root()
    config = load_config(root)

    if args.command == "summary":
        print(summarize_config(config))
        return 0

    if args.command == "auth-help":
        _print_auth_help()
        return 0

    if args.command == "menu":
        _print_menu_file(args.section)
        if args.section == "roles":
            _print_roles_list(config)
        elif args.section == "providers":
            _print_providers_list(config)
        return 0

    if args.command == "role":
        if args.role_cmd == "list":
            _list_roles(config)
            return 0
        if args.role_cmd == "add":
            status = _add_role(config, args.name, args.description)
        elif args.role_cmd == "remove":
            status = _remove_role(config, args.name)
        elif args.role_cmd == "rename":
            status = _rename_role(config, args.old, args.new)
        elif args.role_cmd == "enable":
            status = _set_role_enabled(config, args.name, True)
        elif args.role_cmd == "disable":
            status = _set_role_enabled(config, args.name, False)
        elif args.role_cmd == "set-provider":
            status = _set_role_provider(config, args.name, args.provider)
        elif args.role_cmd == "set-description":
            status = _set_role_description(config, args.name, args.description)
        else:
            status = 1
        if status == 0:
            save_config(root, config)
            print(summarize_config(config))
        return status

    if args.command == "provider":
        if args.provider_cmd == "list":
            print(summarize_config(config))
            return 0
        if args.provider_cmd == "add":
            status = _add_provider(config, args.name, args.kind, args.model, args.command)
        elif args.provider_cmd == "edit":
            status = _edit_provider(config, args.name, args.model, args.command)
        elif args.provider_cmd == "remove":
            status = _remove_provider(config, args.name)
        else:
            status = 1
        if status == 0:
            save_config(root, config)
            print(summarize_config(config))
        return status

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

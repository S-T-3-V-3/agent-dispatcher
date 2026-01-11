#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path

CONFIG_KEY = "aiArchitect"

ROLE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

DEFAULT_CONFIG = {
    "roles": {
        "planning": {
            "enabled": True,
            "provider": "claude",
            "description": "Planning and sequencing work",
        },
        "architect": {
            "enabled": True,
            "provider": "claude",
            "description": "System design and architecture decisions",
        },
        "review": {
            "enabled": True,
            "provider": "claude",
            "description": "Code and design reviews",
        },
        "qa": {
            "enabled": True,
            "provider": "claude",
            "description": "Testing strategy and QA feedback",
        },
    },
    "providers": {
        "claude": {
            "kind": "claude",
            "notes": "Built-in Claude Code agent",
        },
        "codex": {
            "kind": "codex",
            "model": "gpt-5.2-codex",
        },
        "gemini": {
            "kind": "gemini",
            "model": "gemini-1.5-pro",
        },
    },
}


def _find_project_root(start_dir: Path) -> Path:
    start_dir = start_dir.resolve()
    for candidate in [start_dir] + list(start_dir.parents):
        if (candidate / ".claude").is_dir():
            return candidate
    return start_dir


def project_root() -> Path:
    env_root = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_root:
        return Path(env_root).resolve()
    return _find_project_root(Path.cwd())


def settings_path(root: Path) -> Path:
    return root / ".claude" / "settings.json"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return {}


def _deep_merge(base: dict, override: dict) -> dict:
    merged = json.loads(json.dumps(base))
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(root: Path) -> dict:
    settings = _load_json(settings_path(root))
    config = settings.get(CONFIG_KEY, {})
    if not isinstance(config, dict):
        return json.loads(json.dumps(DEFAULT_CONFIG))
    return _deep_merge(DEFAULT_CONFIG, config)


def save_config(root: Path, config: dict) -> None:
    settings_file = settings_path(root)
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    settings = _load_json(settings_file)
    settings[CONFIG_KEY] = config
    with settings_file.open("w", encoding="utf-8") as handle:
        json.dump(settings, handle, indent=2, sort_keys=True)
        handle.write("\n")


def summarize_config(config: dict) -> str:
    roles = config.get("roles", {})
    providers = config.get("providers", {})
    lines = ["Roles:"]
    for role in sorted(roles.keys()):
        role_cfg = roles.get(role, {})
        enabled = "on" if role_cfg.get("enabled", True) else "off"
        provider = role_cfg.get("provider", "claude")
        desc = role_cfg.get("description", "")
        desc_suffix = f" - {desc}" if desc else ""
        lines.append(f"- {role}: {enabled} (provider: {provider}){desc_suffix}")

    lines.append("Providers:")
    for name in sorted(providers.keys()):
        provider = providers.get(name, {})
        kind = provider.get("kind", "custom")
        model = provider.get("model")
        command = provider.get("command")
        extra = []
        if model:
            extra.append(f"model={model}")
        if command:
            extra.append(f"command={command}")
        details = f" ({', '.join(extra)})" if extra else ""
        lines.append(f"- {name} ({kind}){details}")

    return "\n".join(lines)


def validate_role_name(name: str) -> bool:
    return bool(ROLE_NAME_RE.fullmatch(name or ""))

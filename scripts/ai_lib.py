#!/usr/bin/env python3
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

CONFIG_KEY = "aiArchitect"

DEFAULT_CONFIG = {
    "implicit": True,
    "targets": {
        "planning": "codex",
        "architecture": "codex",
        "review": "codex",
    },
    "providers": {
        "codex": {
            "kind": "codex",
            "model": "gpt-5.2-codex",
            "implicit": {
                "sandbox": "read-only",
                "approval": "never",
            },
            "explicit": {
                "sandbox": "workspace-write",
                "approval": "never",
            },
        },
        "gemini": {
            "kind": "gemini",
            "model": "gemini-1.5-pro",
            "implicit": {
                "sandbox": True,
                "approval_mode": "default",
            },
            "explicit": {
                "sandbox": False,
                "approval_mode": "auto_edit",
            },
        },
    },
}

CATEGORIES = ("planning", "architecture", "review")
TARGETS = ("codex", "gemini", "claude", "off")

PLANNING_PATTERNS = re.compile(
    r"\b(plan|planning|roadmap|milestone|scope|timeline|phases|priorit(y|ies)|requirements?)\b",
    re.IGNORECASE,
)
ARCH_PATTERNS = re.compile(
    r"\b(architecture|architect|system design|design\b|tech stack|component(s)?|service(s)?|schema|data model|infrastructure)\b",
    re.IGNORECASE,
)
REVIEW_PATTERNS = re.compile(
    r"\b(review|audit|critique|risk|security review|code review|performance review|refactor)\b",
    re.IGNORECASE,
)


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
    implicit = "on" if config.get("implicit", True) else "off"
    targets = config.get("targets", {})
    lines = [
        f"AI routing (implicit: {implicit})",
        f"- planning: {targets.get('planning', 'codex')}",
        f"- architecture: {targets.get('architecture', 'codex')}",
        f"- review: {targets.get('review', 'codex')}",
        "Providers:",
    ]
    providers = config.get("providers", {})
    for name, provider in providers.items():
        model = provider.get("model")
        implicit_cfg = provider.get("implicit", {})
        explicit_cfg = provider.get("explicit", {})
        kind = provider.get("kind")
        if kind == "codex":
            lines.append(
                f"- {name} (codex, model={model}, implicit sandbox={implicit_cfg.get('sandbox')} approval={implicit_cfg.get('approval')}, explicit sandbox={explicit_cfg.get('sandbox')} approval={explicit_cfg.get('approval')})"
            )
        elif kind == "gemini":
            lines.append(
                f"- {name} (gemini, model={model}, implicit sandbox={implicit_cfg.get('sandbox')} approval_mode={implicit_cfg.get('approval_mode')}, explicit sandbox={explicit_cfg.get('sandbox')} approval_mode={explicit_cfg.get('approval_mode')})"
            )
        elif kind == "command":
            command = provider.get("command")
            lines.append(f"- {name} (command, command={command})")
        else:
            lines.append(f"- {name} (custom provider)")
    return "\n".join(lines)


def classify_prompt(prompt: str) -> str | None:
    if not prompt:
        return None
    if REVIEW_PATTERNS.search(prompt):
        return "review"
    if ARCH_PATTERNS.search(prompt):
        return "architecture"
    if PLANNING_PATTERNS.search(prompt):
        return "planning"
    return None


def build_ai_prompt(category: str, user_prompt: str) -> str:
    base = [
        "You are the primary AI architect. Provide concise, actionable guidance.",
        f"Task category: {category}.",
        "Use the repo context if needed.",
        "Avoid editing files unless the user explicitly asks for changes.",
        "Respond with clear bullet points and a short recommended next step.",
        "",
        "User request:",
        user_prompt.strip(),
    ]
    return "\n".join(base).strip()


def _run_codex(prompt: str, root: Path, mode: str, provider: dict) -> tuple[int, str, str]:
    model = provider.get("model")
    mode_cfg = provider.get(mode, {})
    sandbox = mode_cfg.get("sandbox", "read-only")
    approval = mode_cfg.get("approval", "never")

    cmd = [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "-C",
        str(root),
        "--sandbox",
        str(sandbox),
        "--ask-for-approval",
        str(approval),
    ]
    if model:
        cmd += ["-m", model]

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        output_path = tmp.name

    cmd += ["--output-last-message", output_path, prompt]

    result = subprocess.run(cmd, capture_output=True, text=True)
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    output = ""
    try:
        with open(output_path, "r", encoding="utf-8") as handle:
            output = handle.read().strip()
    except OSError:
        output = ""

    return result.returncode, output, (stderr or stdout)


def _run_gemini(prompt: str, root: Path, mode: str, provider: dict) -> tuple[int, str, str]:
    model = provider.get("model")
    mode_cfg = provider.get(mode, {})
    sandbox = mode_cfg.get("sandbox", False)
    approval_mode = mode_cfg.get("approval_mode", "default")

    cmd = ["gemini", "--output-format", "text"]
    if model:
        cmd += ["-m", model]
    if approval_mode:
        cmd += ["--approval-mode", approval_mode]
    if sandbox:
        cmd += ["--sandbox"]

    cmd.append(prompt)

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(root))
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    return result.returncode, stdout, (stderr or stdout)


def _run_command_provider(prompt: str, root: Path, provider: dict) -> tuple[int, str, str]:
    raw_command = provider.get("command")
    if not raw_command:
        return 1, "", "Missing command for provider."

    if isinstance(raw_command, str):
        command = raw_command.replace("{prompt}", prompt)
        cmd = command if "{prompt}" in raw_command else f"{command} \"{prompt}\""
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(root), shell=True)
    else:
        cmd_list = [str(item) for item in raw_command]
        if "{prompt}" in cmd_list:
            cmd_list = [prompt if item == "{prompt}" else item for item in cmd_list]
        else:
            cmd_list.append(prompt)
        result = subprocess.run(cmd_list, capture_output=True, text=True, cwd=str(root))

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    return result.returncode, stdout, (stderr or stdout)


def run_provider(provider_name: str, prompt: str, root: Path, mode: str, config: dict) -> tuple[int, str, str]:
    providers = config.get("providers", {})
    provider = providers.get(provider_name)
    if not provider:
        return 1, "", f"Unknown provider: {provider_name}"

    kind = provider.get("kind")
    if kind == "codex":
        return _run_codex(prompt, root, mode, provider)
    if kind == "gemini":
        return _run_gemini(prompt, root, mode, provider)
    if kind == "command":
        return _run_command_provider(prompt, root, provider)

    return 1, "", f"Unsupported provider kind: {kind}"

#!/usr/bin/env python3
import argparse
import sys

from ai_lib import CATEGORIES, TARGETS, load_config, project_root, save_config, summarize_config


def _prompt(text: str) -> str:
    return input(text).strip()


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
    print("")
    print("Custom providers:")
    print("- Provide a command that accepts a prompt argument, or use {prompt} placeholder.")
    print("- Example command array: [\"mycli\", \"--prompt\", \"{prompt}\"]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage AI routing settings")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("config", help="Interactive configuration")
    sub.add_parser("summary", help="Show current routing configuration")

    set_target = sub.add_parser("set-target", help="Set routing target for a category")
    set_target.add_argument("category", choices=CATEGORIES)
    set_target.add_argument("target", choices=TARGETS)

    set_implicit = sub.add_parser("set-implicit", help="Enable or disable implicit routing")
    set_implicit.add_argument("state", choices=("on", "off"))

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = project_root()
    config = load_config(root)

    if args.command == "config":
        if not sys.stdin.isatty():
            print("Interactive configuration requires a TTY.")
            print("Run this command in a terminal:")
            print("python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ai_config.py config")
            return 0

        while True:
            print("")
            print("AI routing configuration")
            print("1) Show current config")
            print("2) Toggle implicit routing")
            print("3) Set category target")
            print("4) Add custom provider")
            print("5) Remove custom provider")
            print("6) Auth / install help for Codex & Gemini")
            print("7) Save and exit")
            choice = _prompt("> ")

            if choice == "1":
                print(summarize_config(config))
            elif choice == "2":
                current = "on" if config.get("implicit", True) else "off"
                print(f"Implicit routing is currently {current}.")
                new_state = _prompt("Set implicit to on/off: ").lower()
                if new_state in ("on", "off"):
                    config["implicit"] = new_state == "on"
                else:
                    print("Invalid option.")
            elif choice == "3":
                category = _prompt(f"Category {CATEGORIES}: ").lower()
                if category not in CATEGORIES:
                    print("Invalid category.")
                    continue
                target = _prompt(f"Target {TARGETS}: ").lower()
                if target not in TARGETS:
                    print("Invalid target.")
                    continue
                config.setdefault("targets", {})[category] = target
            elif choice == "4":
                name = _prompt("Provider name: ")
                if not name:
                    print("Name required.")
                    continue
                cmd = _prompt("Command (use {prompt} placeholder if needed): ")
                if not cmd:
                    print("Command required.")
                    continue
                config.setdefault("providers", {})[name] = {
                    "kind": "command",
                    "command": cmd,
                }
            elif choice == "5":
                name = _prompt("Provider name to remove: ")
                if name in ("codex", "gemini"):
                    print("Cannot remove built-in providers.")
                    continue
                providers = config.get("providers", {})
                if name in providers:
                    providers.pop(name)
                else:
                    print("Provider not found.")
            elif choice == "6":
                _print_auth_help()
            elif choice == "7":
                save_config(root, config)
                print(f"Saved settings at {root / '.claude' / 'settings.json'}")
                print(summarize_config(config))
                return 0
            else:
                print("Unknown selection.")

    if args.command == "summary":
        print(summarize_config(config))
        return 0

    if args.command == "set-target":
        config.setdefault("targets", {})[args.category] = args.target
        save_config(root, config)
        print(summarize_config(config))
        return 0

    if args.command == "set-implicit":
        config["implicit"] = args.state == "on"
        save_config(root, config)
        print(summarize_config(config))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

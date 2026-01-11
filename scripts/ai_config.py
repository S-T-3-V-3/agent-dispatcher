#!/usr/bin/env python3
import argparse

from ai_lib import CATEGORIES, TARGETS, load_config, project_root, save_config, summarize_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage AI routing settings")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup", help="Initialize settings with defaults")
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

    if args.command == "setup":
        save_config(root, config)
        print(f"Initialized settings at {root / '.claude' / 'settings.json'}")
        print(summarize_config(config))
        return 0

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

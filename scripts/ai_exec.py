#!/usr/bin/env python3
import argparse
import sys

from ai_lib import build_ai_prompt, load_config, project_root, run_provider


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a provider for a specific category")
    parser.add_argument("--category", choices=("planning", "architecture", "review"), required=True)
    parser.add_argument("--mode", choices=("implicit", "explicit"), default="explicit")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--prompt", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    user_prompt = args.prompt
    if not user_prompt:
        user_prompt = sys.stdin.read().strip()
    if not user_prompt:
        user_prompt = f"Provide {args.category} guidance based on the current project."

    root = project_root()
    config = load_config(root)
    target = args.provider or config.get("targets", {}).get(args.category, "codex")

    if target in ("claude", "off"):
        print(f"Routing target for {args.category} is '{target}'. No external provider invoked.")
        return 0

    prompt = build_ai_prompt(args.category, user_prompt)
    status, output, error = run_provider(target, prompt, root, args.mode, config)

    if status != 0:
        print("Provider invocation failed. Falling back to Claude.")
        if error:
            print(f"Provider error: {error}")
        return 0

    if not output:
        print("Provider produced no output. Falling back to Claude.")
        return 0

    print(f"Provider output ({target}, {args.category}):")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

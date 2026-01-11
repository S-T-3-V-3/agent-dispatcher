#!/usr/bin/env python3
import json
import sys

from ai_lib import build_ai_prompt, classify_prompt, load_config, project_root, run_provider


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    prompt = payload.get("prompt", "") or ""
    category = classify_prompt(prompt)
    if not category:
        return 0

    root = project_root()
    config = load_config(root)
    if not config.get("implicit", True):
        return 0

    target = config.get("targets", {}).get(category, "codex")
    if target in ("claude", "off"):
        return 0

    provider_prompt = build_ai_prompt(category, prompt)
    status, output, error = run_provider(target, provider_prompt, root, "implicit", config)

    if status != 0:
        print("Provider routing failed; continue with Claude.")
        if error:
            print(f"Provider error: {error}")
        return 0

    if not output:
        print("Provider routing produced no output; continue with Claude.")
        return 0

    print("Provider routing (use as primary guidance):")
    print(f"Category: {category}")
    print(f"Provider: {target}")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

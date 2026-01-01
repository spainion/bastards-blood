#!/usr/bin/env python3
"""Lightweight OpenRouter chat helper for local/dev use."""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def chat(model: str, system: str, user: str, api_key: str, base_url: str) -> dict:
    """Send a chat completion request to OpenRouter."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system or ""},
            {"role": "user", "content": user},
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        return {"error": f"HTTP {exc.code}", "details": exc.read().decode("utf-8", errors="replace")}
    except Exception as exc:  # pragma: no cover - defensive
        return {"error": str(exc)}


def main():
    parser = argparse.ArgumentParser(description="OpenRouter chat tester")
    parser.add_argument("--model", default="anthropic/claude-3.5-sonnet")
    parser.add_argument("--system", default="", help="System message")
    parser.add_argument("--user", required=True, help="User message")
    parser.add_argument(
        "--api-key-env",
        default="OPENROUTER_API_KEY",
        help="Environment variable holding the OpenRouter API key",
    )
    parser.add_argument(
        "--base-url",
        default="https://openrouter.ai/api/v1/chat/completions",
        help="Override OpenRouter base URL",
    )

    args = parser.parse_args()
    api_key = os.getenv(args.api_key_env)
    if not api_key:
        print(f"Missing API key env: {args.api_key_env}", file=sys.stderr)
        return 1

    result = chat(args.model, args.system, args.user, api_key, args.base_url)
    print(json.dumps(result, indent=2))
    with open("/tmp/openrouter_result.json", "w") as f:
        json.dump(result, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Dev workbench to send context + prompt through OpenRouter."""

import argparse
import json
import os
import sys

from context_engine import build_full_game_state, build_character_focused, build_session_focused, build_combat_focused, build_narrative_focused, build_world_focused
from prompt_engine import generate_prompt
from openrouter_client import chat


CONTEXT_BUILDERS = {
    "full_game_state": lambda max_tokens, include_memories, recent: build_full_game_state(max_tokens, include_memories, recent),
    "character_focused": lambda max_tokens, include_memories, recent, focus=None: build_character_focused(focus or [], max_tokens, include_memories, recent),
    "session_focused": lambda max_tokens, include_memories, recent, focus=None: build_session_focused(focus or [], max_tokens, include_memories, recent),
    "combat_focused": lambda max_tokens, include_memories, recent, focus=None: build_combat_focused(focus or [], max_tokens, include_memories, recent),
    "narrative_focused": lambda max_tokens, include_memories, recent, focus=None: build_narrative_focused(focus or [], max_tokens, include_memories, recent),
    "world_focused": lambda max_tokens, include_memories, recent, focus=None: build_world_focused(focus or [], max_tokens, include_memories, recent),
}


def build_context(context_type: str, focus_ids, max_tokens: int, include_memories: bool, recent_events: int):
    builder = CONTEXT_BUILDERS.get(context_type, CONTEXT_BUILDERS["full_game_state"])
    if context_type == "full_game_state":
        return builder(max_tokens, include_memories, recent_events)
    return builder(max_tokens, include_memories, recent_events, focus_ids)


def main():
    parser = argparse.ArgumentParser(description="Dev OpenRouter runner for context + prompts")
    parser.add_argument("--context-type", default="full_game_state", choices=list(CONTEXT_BUILDERS.keys()))
    parser.add_argument("--focus-ids", default="", help="Comma-separated IDs for focused contexts")
    parser.add_argument("--max-tokens", type=int, default=4000)
    parser.add_argument("--include-memories", default="true")
    parser.add_argument("--recent-events", type=int, default=20)
    parser.add_argument("--prompt-type", default="narration")
    parser.add_argument("--template-id", default="")
    parser.add_argument("--variables-file", help="Path to prompt variables JSON")
    parser.add_argument("--model", default="anthropic/claude-3.5-sonnet")
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--base-url", default="https://openrouter.ai/api/v1/chat/completions")
    args = parser.parse_args()

    api_key = os.getenv(args.api_key_env)
    if not api_key:
        print(f"Missing API key env: {args.api_key_env}", file=sys.stderr)
        return 1

    focus_ids = [fid.strip() for fid in args.focus_ids.split(",") if fid.strip()]
    include_memories = args.include_memories.lower() == "true"

    variables = {}
    if args.variables_file and os.path.exists(args.variables_file):
        with open(args.variables_file, "r") as f:
            variables = json.load(f)

    context = build_context(args.context_type, focus_ids, args.max_tokens, include_memories, args.recent_events)
    prompt_id = args.template_id or args.prompt_type
    prompt = generate_prompt(prompt_id, variables, include_context=False, model_hints={"provider": "openrouter"})

    user_message = prompt.get("user_prompt", "")
    if context:
        user_message += "\n\nContext:\n" + json.dumps(context, indent=2)

    result = chat(args.model, prompt.get("system_prompt", ""), user_message, api_key, args.base_url)

    output = {
        "model": args.model,
        "prompt": prompt,
        "context_summary": {
            "type": context.get("type"),
            "estimated_tokens": context.get("estimated_tokens"),
            "within_limit": context.get("within_limit"),
        },
        "openrouter_response": result,
    }

    with open("/tmp/dev_openrouter_result.json", "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

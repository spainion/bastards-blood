#!/usr/bin/env python3
"""Get the current game state by reducing session events."""

import argparse
import copy
import json
import os
import sys


def load_all_characters() -> dict:
    """Load all character files into a dictionary."""
    characters = {}
    chars_dir = "data/characters"
    
    if os.path.exists(chars_dir):
        for filename in os.listdir(chars_dir):
            if filename.endswith('.json'):
                with open(os.path.join(chars_dir, filename), 'r') as f:
                    char = json.load(f)
                    if 'id' in char:
                        characters[char['id']] = char
    
    return characters


def load_session(session_id: str) -> dict:
    """Load a session file."""
    session_path = f"data/sessions/{session_id}.json"
    if not os.path.exists(session_path):
        raise FileNotFoundError(f"Session not found: {session_path}")
    
    with open(session_path, 'r') as f:
        return json.load(f)


def reduce(state: dict, event: dict) -> dict:
    """Apply an event to the state and return the new state."""
    s = copy.deepcopy(state)
    t = event.get("t")
    d = event.get("data", {})
    r = event.get("result", {})
    
    if t == "create_char":
        c = d.get("character")
        if c and "id" in c:
            s["characters"][c["id"]] = c
    
    elif t == "update_char":
        cid = d.get("id")
        patch = d.get("patch", {})
        if cid in s["characters"] and isinstance(patch, dict):
            allowed = {"id", "name", "class", "lvl", "stats", "hp", "inventory", "tags", "notes"}
            filtered_patch = {k: v for k, v in patch.items() if k in allowed}
            if filtered_patch:
                s["characters"][cid].update(filtered_patch)
    
    elif t == "gain_item":
        cid = d.get("id")
        item = d.get("item")
        if cid in s["characters"] and item is not None:
            s["characters"][cid].setdefault("inventory", []).append(item)
    
    elif t == "lose_item":
        cid = d.get("id")
        item = d.get("item")
        if cid in s["characters"] and item is not None:
            inv = s["characters"][cid].setdefault("inventory", [])
            if item in inv:
                inv.remove(item)
    
    elif t == "damage":
        cid = d.get("id")
        amt = r.get("amount", d.get("amount", 0))
        char = s["characters"].get(cid) if cid else None
        if char:
            hp = char.get("hp", {})
            if "current" in hp:
                hp["current"] = max(0, hp.get("current", 0) - amt)
                char["hp"] = hp
                s["characters"][cid] = char
    
    elif t == "heal":
        cid = d.get("id")
        amt = r.get("amount", d.get("amount", 0))
        char = s["characters"].get(cid) if cid else None
        if char:
            hp = char.get("hp", {})
            if "current" in hp and "max" in hp:
                hp["current"] = min(hp["max"], hp.get("current", 0) + amt)
                char["hp"] = hp
                s["characters"][cid] = char
    
    return s


def generate_summary(state: dict) -> dict:
    """Generate a summary of the game state."""
    summary = {
        "total_characters": len(state.get("characters", {})),
        "characters": []
    }
    
    for char_id, char in state.get("characters", {}).items():
        char_summary = {
            "id": char_id,
            "name": char.get("name", "Unknown"),
            "class": char.get("class", "Unknown"),
            "level": char.get("lvl", 1),
            "hp": f"{char.get('hp', {}).get('current', 0)}/{char.get('hp', {}).get('max', 0)}",
            "tags": char.get("tags", [])
        }
        summary["characters"].append(char_summary)
    
    return summary


def main():
    parser = argparse.ArgumentParser(description='Get the current game state')
    parser.add_argument('--session', required=True, help='Session ID')
    parser.add_argument('--format', choices=['summary', 'full'], default='summary',
                       help='Output format')
    
    args = parser.parse_args()
    
    # Load base state from character files
    state = {"characters": load_all_characters()}
    
    # Load and apply session events
    session = load_session(args.session)
    for event in session.get("events", []):
        state = reduce(state, event)
    
    # Output result
    if args.format == 'summary':
        output = generate_summary(state)
    else:
        output = state
    
    print(json.dumps(output, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

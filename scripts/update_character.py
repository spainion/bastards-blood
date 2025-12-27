#!/usr/bin/env python3
"""Update an existing character."""

import argparse
import json
import os
import sys


ALLOWED_FIELDS = {'id', 'name', 'class', 'lvl', 'stats', 'hp', 'inventory', 'tags', 'notes'}


def load_character(char_id: str) -> dict:
    """Load a character file."""
    char_path = f"data/characters/{char_id}.json"
    if not os.path.exists(char_path):
        raise FileNotFoundError(f"Character not found: {char_path}")
    
    with open(char_path, 'r') as f:
        return json.load(f)


def save_character(char_id: str, character: dict):
    """Save a character file."""
    char_path = f"data/characters/{char_id}.json"
    with open(char_path, 'w') as f:
        json.dump(character, f, indent=2)


def apply_patch(character: dict, patch: dict) -> dict:
    """Apply a patch to a character, only allowing valid fields."""
    for key, value in patch.items():
        if key not in ALLOWED_FIELDS:
            print(f"Warning: Ignoring invalid field '{key}'", file=sys.stderr)
            continue
        
        if key == 'id' and value != character.get('id'):
            print(f"Warning: Cannot change character ID", file=sys.stderr)
            continue
        
        # Handle nested updates for stats and hp
        if key in ('stats', 'hp') and isinstance(value, dict):
            if key not in character:
                character[key] = {}
            character[key].update(value)
        else:
            character[key] = value
    
    return character


def main():
    parser = argparse.ArgumentParser(description='Update an existing character')
    parser.add_argument('--id', required=True, help='Character ID to update')
    parser.add_argument('--patch-file', required=True, help='Path to JSON file containing patch')
    
    args = parser.parse_args()
    
    # Load patch from file
    with open(args.patch_file, 'r') as f:
        patch = json.load(f)
    
    # Load character
    character = load_character(args.id)
    
    # Apply patch
    character = apply_patch(character, patch)
    
    # Save character
    save_character(args.id, character)
    
    print(f"Updated character: {args.id}")
    print(json.dumps(character, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

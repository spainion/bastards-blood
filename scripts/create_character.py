#!/usr/bin/env python3
"""Create a new character JSON file."""

import argparse
import json
import os
import sys


def parse_list(value: str) -> list:
    """Parse comma-separated string into list."""
    if not value or value.strip() == '':
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


def create_character(
    char_id: str,
    name: str,
    char_class: str,
    level: int,
    stats: dict,
    hp_max: int,
    inventory: list,
    tags: list,
    notes: str
) -> dict:
    """Create a character dictionary."""
    character = {
        "id": char_id,
        "name": name,
        "class": char_class,
        "lvl": level,
        "stats": stats,
        "hp": {
            "max": hp_max,
            "current": hp_max
        },
        "inventory": inventory,
        "tags": tags,
        "notes": notes
    }
    return character


def main():
    parser = argparse.ArgumentParser(description='Create a new character')
    parser.add_argument('--id', required=True, help='Character ID')
    parser.add_argument('--name', required=True, help='Character name')
    parser.add_argument('--class', dest='char_class', default='Adventurer', help='Character class')
    parser.add_argument('--level', type=int, default=1, help='Character level')
    parser.add_argument('--str', type=int, default=10, help='Strength stat')
    parser.add_argument('--dex', type=int, default=10, help='Dexterity stat')
    parser.add_argument('--con', type=int, default=10, help='Constitution stat')
    parser.add_argument('--int', type=int, default=10, help='Intelligence stat')
    parser.add_argument('--wis', type=int, default=10, help='Wisdom stat')
    parser.add_argument('--cha', type=int, default=10, help='Charisma stat')
    parser.add_argument('--hp-max', type=int, default=10, help='Maximum HP')
    parser.add_argument('--inventory', default='', help='Comma-separated inventory items')
    parser.add_argument('--tags', default='npc', help='Comma-separated tags')
    parser.add_argument('--notes', default='', help='Character notes')
    
    args = parser.parse_args()
    
    stats = {
        "STR": getattr(args, 'str'),
        "DEX": args.dex,
        "CON": args.con,
        "INT": getattr(args, 'int'),
        "WIS": args.wis,
        "CHA": args.cha
    }
    
    character = create_character(
        char_id=args.id,
        name=args.name,
        char_class=args.char_class,
        level=args.level,
        stats=stats,
        hp_max=args.hp_max,
        inventory=parse_list(args.inventory),
        tags=parse_list(args.tags),
        notes=args.notes
    )
    
    # Write to file
    output_path = f"data/characters/{args.id}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(character, f, indent=2)
    
    print(f"Created character: {output_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())

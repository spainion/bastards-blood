#!/usr/bin/env python3
"""Execute batch operations on multiple characters."""

import argparse
import json
import os
import random
import string
import sys
from datetime import datetime, timezone


def generate_event_id():
    """Generate a unique event ID."""
    chars = string.ascii_lowercase + string.digits
    suffix = ''.join(random.choice(chars) for _ in range(8))
    return f"e_{suffix}"


def load_character(char_id):
    """Load a character file."""
    path = f"data/characters/{char_id}.json"
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None


def save_character(char_id, char):
    """Save a character file."""
    path = f"data/characters/{char_id}.json"
    with open(path, 'w') as f:
        json.dump(char, f, indent=2)


def load_session(session_id):
    """Load a session file."""
    path = f"data/sessions/{session_id}.json"
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None


def save_session(session_id, session):
    """Save a session file."""
    path = f"data/sessions/{session_id}.json"
    with open(path, 'w') as f:
        json.dump(session, f, indent=2)


def create_event(event_type, actor, target, data, result):
    """Create an event object."""
    event = {
        "id": generate_event_id(),
        "ts": datetime.now(timezone.utc).isoformat(),
        "t": event_type
    }
    if actor:
        event["actor"] = actor
    if target:
        event["target"] = target
    if data:
        event["data"] = data
    if result:
        event["result"] = result
    return event


def bulk_damage(targets, session_id, params):
    """Apply damage to multiple characters."""
    amount = params.get('amount', 0)
    damage_type = params.get('damage_type', 'untyped')
    results = []
    session = load_session(session_id)
    
    for char_id in targets:
        char = load_character(char_id)
        if char:
            old_hp = char.get('hp', {}).get('current', 0)
            new_hp = max(0, old_hp - amount)
            char['hp']['current'] = new_hp
            save_character(char_id, char)
            
            result = {
                "character": char_id,
                "old_hp": old_hp,
                "new_hp": new_hp,
                "damage": amount
            }
            results.append(result)
            
            # Log event
            if session:
                event = create_event(
                    "damage", "gm", char_id,
                    {"amount": amount, "type": damage_type},
                    {"old_hp": old_hp, "new_hp": new_hp}
                )
                session['events'].append(event)
    
    if session:
        save_session(session_id, session)
    
    return {"operation": "bulk_damage", "results": results}


def bulk_heal(targets, session_id, params):
    """Heal multiple characters."""
    amount = params.get('amount', 0)
    results = []
    session = load_session(session_id)
    
    for char_id in targets:
        char = load_character(char_id)
        if char:
            old_hp = char.get('hp', {}).get('current', 0)
            max_hp = char.get('hp', {}).get('max', old_hp)
            new_hp = min(max_hp, old_hp + amount)
            char['hp']['current'] = new_hp
            save_character(char_id, char)
            
            result = {
                "character": char_id,
                "old_hp": old_hp,
                "new_hp": new_hp,
                "healed": new_hp - old_hp
            }
            results.append(result)
            
            if session:
                event = create_event(
                    "heal", "gm", char_id,
                    {"amount": amount},
                    {"old_hp": old_hp, "new_hp": new_hp}
                )
                session['events'].append(event)
    
    if session:
        save_session(session_id, session)
    
    return {"operation": "bulk_heal", "results": results}


def distribute_items(targets, session_id, params):
    """Distribute items to multiple characters."""
    items = params.get('items', [])
    results = []
    session = load_session(session_id)
    
    for char_id in targets:
        char = load_character(char_id)
        if char:
            inventory = char.setdefault('inventory', [])
            added_items = []
            for item in items:
                inventory.append(item)
                added_items.append(item)
            save_character(char_id, char)
            
            result = {"character": char_id, "items_added": added_items}
            results.append(result)
            
            if session:
                for item in added_items:
                    event = create_event(
                        "gain_item", "gm", char_id,
                        {"id": char_id, "item": item},
                        {}
                    )
                    session['events'].append(event)
    
    if session:
        save_session(session_id, session)
    
    return {"operation": "distribute_items", "results": results}


def apply_status(targets, session_id, params):
    """Apply status effect to multiple characters."""
    status = params.get('status', 'unknown')
    duration = params.get('duration', 'indefinite')
    results = []
    session = load_session(session_id)
    
    for char_id in targets:
        char = load_character(char_id)
        if char:
            tags = char.setdefault('tags', [])
            status_tag = f"status:{status}"
            if status_tag not in tags:
                tags.append(status_tag)
            save_character(char_id, char)
            
            result = {"character": char_id, "status": status, "duration": duration}
            results.append(result)
            
            if session:
                event = create_event(
                    "status", "gm", char_id,
                    {"status": status, "duration": duration},
                    {"applied": True}
                )
                session['events'].append(event)
    
    if session:
        save_session(session_id, session)
    
    return {"operation": "apply_status", "results": results}


def level_up(targets, session_id, params):
    """Level up multiple characters."""
    levels = params.get('levels', 1)
    hp_increase = params.get('hp_increase', 5)
    results = []
    session = load_session(session_id)
    
    for char_id in targets:
        char = load_character(char_id)
        if char:
            old_level = char.get('lvl', 1)
            new_level = old_level + levels
            char['lvl'] = new_level
            
            # Increase HP
            old_max_hp = char.get('hp', {}).get('max', 0)
            new_max_hp = old_max_hp + (hp_increase * levels)
            char['hp']['max'] = new_max_hp
            char['hp']['current'] = new_max_hp  # Full heal on level up
            
            save_character(char_id, char)
            
            result = {
                "character": char_id,
                "old_level": old_level,
                "new_level": new_level,
                "new_max_hp": new_max_hp
            }
            results.append(result)
            
            if session:
                event = create_event(
                    "update_char", "gm", char_id,
                    {"id": char_id, "patch": {"lvl": new_level, "hp": char['hp']}},
                    {"leveled_up": True}
                )
                session['events'].append(event)
    
    if session:
        save_session(session_id, session)
    
    return {"operation": "level_up", "results": results}


def reset_hp(targets, session_id, params):
    """Reset HP to max for multiple characters."""
    results = []
    session = load_session(session_id)
    
    for char_id in targets:
        char = load_character(char_id)
        if char:
            max_hp = char.get('hp', {}).get('max', 0)
            old_hp = char.get('hp', {}).get('current', 0)
            char['hp']['current'] = max_hp
            save_character(char_id, char)
            
            result = {
                "character": char_id,
                "old_hp": old_hp,
                "new_hp": max_hp
            }
            results.append(result)
            
            if session:
                event = create_event(
                    "heal", "gm", char_id,
                    {"full_heal": True},
                    {"old_hp": old_hp, "new_hp": max_hp}
                )
                session['events'].append(event)
    
    if session:
        save_session(session_id, session)
    
    return {"operation": "reset_hp", "results": results}


def main():
    parser = argparse.ArgumentParser(description='Execute batch operations')
    parser.add_argument('--operation', required=True,
                       choices=['bulk_damage', 'bulk_heal', 'distribute_items',
                               'apply_status', 'level_up', 'reset_hp'])
    parser.add_argument('--targets', required=True, help='Comma-separated character IDs')
    parser.add_argument('--session', required=True, help='Session ID')
    parser.add_argument('--params-file', help='Path to JSON params file')
    
    args = parser.parse_args()
    
    targets = [t.strip() for t in args.targets.split(',') if t.strip()]
    
    params = {}
    if args.params_file and os.path.exists(args.params_file):
        with open(args.params_file, 'r') as f:
            params = json.load(f)
    
    handlers = {
        'bulk_damage': bulk_damage,
        'bulk_heal': bulk_heal,
        'distribute_items': distribute_items,
        'apply_status': apply_status,
        'level_up': level_up,
        'reset_hp': reset_hp
    }
    
    result = handlers[args.operation](targets, args.session, params)
    
    with open('/tmp/batch_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

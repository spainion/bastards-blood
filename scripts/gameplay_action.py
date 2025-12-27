#!/usr/bin/env python3
"""Execute gameplay actions and log them to session."""

import argparse
import json
import os
import random
import string
import sys
from datetime import datetime, timezone


def generate_event_id() -> str:
    """Generate a unique event ID."""
    chars = string.ascii_lowercase + string.digits
    suffix = ''.join(random.choice(chars) for _ in range(8))
    return f"e_{suffix}"


def roll_dice(dice_str: str) -> tuple:
    """Roll dice and return (total, rolls). Format: NdM+B (e.g., 2d6+3)."""
    import re
    match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice_str.lower())
    if not match:
        return 0, []
    
    num_dice = int(match.group(1))
    die_size = int(match.group(2))
    bonus = int(match.group(3)) if match.group(3) else 0
    
    rolls = [random.randint(1, die_size) for _ in range(num_dice)]
    total = sum(rolls) + bonus
    return total, rolls


def load_character(char_id: str) -> dict:
    """Load a character file."""
    char_path = f"data/characters/{char_id}.json"
    if not os.path.exists(char_path):
        return None
    with open(char_path, 'r') as f:
        return json.load(f)


def load_session(session_id: str) -> dict:
    """Load a session file."""
    session_path = f"data/sessions/{session_id}.json"
    if not os.path.exists(session_path):
        raise FileNotFoundError(f"Session not found: {session_path}")
    with open(session_path, 'r') as f:
        return json.load(f)


def save_session(session_id: str, session: dict):
    """Save a session file."""
    session_path = f"data/sessions/{session_id}.json"
    with open(session_path, 'w') as f:
        json.dump(session, f, indent=2)


def get_stat_modifier(stat_value: int) -> int:
    """Calculate D&D-style stat modifier."""
    return (stat_value - 10) // 2


def execute_roll(actor: dict, params: dict) -> dict:
    """Execute a dice roll action."""
    dice = params.get('dice', '1d20')
    stat = params.get('stat')
    
    total, rolls = roll_dice(dice)
    result = {
        "dice": dice,
        "rolls": rolls,
        "total": total
    }
    
    # Add stat modifier if specified
    if stat and actor:
        stat_value = actor.get('stats', {}).get(stat.upper(), 10)
        modifier = get_stat_modifier(stat_value)
        result["stat"] = stat.upper()
        result["modifier"] = modifier
        result["final"] = total + modifier
    
    return result


def execute_attack(actor: dict, target: dict, params: dict) -> dict:
    """Execute an attack action."""
    # Roll to hit (1d20 + DEX or STR modifier)
    attack_stat = params.get('attack_stat', 'STR')
    stat_value = actor.get('stats', {}).get(attack_stat.upper(), 10) if actor else 10
    attack_modifier = get_stat_modifier(stat_value)
    
    attack_roll, attack_rolls = roll_dice('1d20')
    attack_total = attack_roll + attack_modifier
    
    # Simple AC calculation (10 + DEX modifier for target)
    target_dex = target.get('stats', {}).get('DEX', 10) if target else 10
    target_ac = 10 + get_stat_modifier(target_dex)
    
    hit = attack_total >= target_ac
    
    result = {
        "attack_roll": attack_roll,
        "attack_modifier": attack_modifier,
        "attack_total": attack_total,
        "target_ac": target_ac,
        "hit": hit
    }
    
    # Roll damage if hit
    if hit:
        damage_dice = params.get('damage_dice', '1d6')
        damage, damage_rolls = roll_dice(damage_dice)
        result["damage_dice"] = damage_dice
        result["damage_rolls"] = damage_rolls
        result["damage"] = damage
    
    return result


def execute_cast_spell(actor: dict, target: dict, params: dict) -> dict:
    """Execute a spell casting action."""
    spell_name = params.get('spell_name', 'Unknown Spell')
    spell_level = params.get('spell_level', 0)
    
    # Spell attack or save
    save_dc = 8 + get_stat_modifier(actor.get('stats', {}).get('INT', 10)) if actor else 10
    
    result = {
        "spell_name": spell_name,
        "spell_level": spell_level,
        "save_dc": save_dc
    }
    
    # Roll effect if applicable
    effect_dice = params.get('effect_dice')
    if effect_dice:
        effect, effect_rolls = roll_dice(effect_dice)
        result["effect_dice"] = effect_dice
        result["effect_rolls"] = effect_rolls
        result["effect"] = effect
    
    return result


def execute_use_item(actor: dict, params: dict) -> dict:
    """Execute an item use action."""
    item_name = params.get('item_name', 'Unknown Item')
    
    result = {
        "item_name": item_name,
        "used": True
    }
    
    # Roll effect if applicable
    effect_dice = params.get('effect_dice')
    if effect_dice:
        effect, effect_rolls = roll_dice(effect_dice)
        result["effect_dice"] = effect_dice
        result["effect_rolls"] = effect_rolls
        result["effect"] = effect
    
    return result


def execute_rest(actor: dict, params: dict) -> dict:
    """Execute a rest action."""
    rest_type = params.get('rest_type', 'short')
    
    result = {
        "rest_type": rest_type
    }
    
    if actor:
        hp = actor.get('hp', {})
        current = hp.get('current', 0)
        max_hp = hp.get('max', current)
        
        if rest_type == 'long':
            # Full heal on long rest
            result["hp_restored"] = max_hp - current
            result["new_hp"] = max_hp
        else:
            # Short rest: restore some HP
            con_mod = get_stat_modifier(actor.get('stats', {}).get('CON', 10))
            heal = max(1, con_mod + random.randint(1, 6))
            new_hp = min(max_hp, current + heal)
            result["hp_restored"] = new_hp - current
            result["new_hp"] = new_hp
    
    return result


def execute_travel(actor: dict, params: dict) -> dict:
    """Execute a travel action."""
    destination = params.get('destination', 'Unknown')
    distance = params.get('distance', 0)
    
    result = {
        "destination": destination,
        "distance": distance
    }
    
    # Random encounter check
    encounter_roll = random.randint(1, 20)
    result["encounter_check"] = encounter_roll
    result["encounter"] = encounter_roll == 1  # 5% chance
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Execute a gameplay action')
    parser.add_argument('--action', required=True, 
                       choices=['roll', 'attack', 'cast_spell', 'use_item', 'rest', 'travel'],
                       help='Action type')
    parser.add_argument('--session', required=True, help='Session ID')
    parser.add_argument('--actor', required=True, help='Actor character ID')
    parser.add_argument('--target', default='', help='Target character ID')
    parser.add_argument('--params-file', help='Path to JSON file containing parameters')
    
    args = parser.parse_args()
    
    # Load parameters
    params = {}
    if args.params_file and os.path.exists(args.params_file):
        with open(args.params_file, 'r') as f:
            params = json.load(f)
    
    # Load actor and target characters
    actor = load_character(args.actor)
    target = load_character(args.target) if args.target else None
    
    # Execute action
    action_handlers = {
        'roll': lambda: execute_roll(actor, params),
        'attack': lambda: execute_attack(actor, target, params),
        'cast_spell': lambda: execute_cast_spell(actor, target, params),
        'use_item': lambda: execute_use_item(actor, params),
        'rest': lambda: execute_rest(actor, params),
        'travel': lambda: execute_travel(actor, params)
    }
    
    result = action_handlers[args.action]()
    
    # Map action to event type
    action_to_event = {
        'roll': 'check',
        'attack': 'attack',
        'cast_spell': 'custom',
        'use_item': 'custom',
        'rest': 'heal',
        'travel': 'custom'
    }
    
    event_type = action_to_event[args.action]
    
    # Create event
    event = {
        "id": generate_event_id(),
        "ts": datetime.now(timezone.utc).isoformat(),
        "t": event_type,
        "actor": args.actor,
        "data": {
            "action": args.action,
            "params": params
        },
        "result": result
    }
    
    if args.target:
        event["target"] = args.target
    
    # Load session and append event
    session = load_session(args.session)
    session['events'].append(event)
    save_session(args.session, session)
    
    # Save result for workflow summary
    with open('/tmp/action_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Action executed: {args.action}")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

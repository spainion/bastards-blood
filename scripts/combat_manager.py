#!/usr/bin/env python3
"""Combat manager for turn-based combat tracking."""

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


def get_combat_state_file():
    """Get the path to the combat state file."""
    return "data/combat_state.json"


def load_combat_state():
    """Load current combat state."""
    path = get_combat_state_file()
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None


def save_combat_state(state):
    """Save combat state."""
    path = get_combat_state_file()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(state, f, indent=2)


def clear_combat_state():
    """Clear combat state file."""
    path = get_combat_state_file()
    if os.path.exists(path):
        os.remove(path)


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


def roll_initiative(char):
    """Roll initiative for a character."""
    dex = char.get('stats', {}).get('DEX', 10)
    modifier = (dex - 10) // 2
    roll = random.randint(1, 20)
    return roll + modifier


def start_combat(session_id, combatants, params):
    """Start a new combat encounter."""
    session = load_session(session_id)
    
    # Roll initiative for all combatants
    initiative_order = []
    for char_id in combatants:
        char = load_character(char_id)
        if char:
            init = roll_initiative(char)
            initiative_order.append({
                "id": char_id,
                "name": char.get('name', char_id),
                "initiative": init,
                "hp": char.get('hp', {}).get('current', 0),
                "max_hp": char.get('hp', {}).get('max', 0)
            })
    
    # Sort by initiative (descending)
    initiative_order.sort(key=lambda x: x['initiative'], reverse=True)
    
    combat_state = {
        "active": True,
        "session_id": session_id,
        "round": 1,
        "turn_index": 0,
        "combatants": initiative_order,
        "started_at": datetime.now(timezone.utc).isoformat()
    }
    
    save_combat_state(combat_state)
    
    # Log event
    if session:
        event = create_event(
            "custom", "gm", None,
            {"action": "start_combat", "combatants": combatants},
            {"initiative_order": initiative_order}
        )
        session['events'].append(event)
        save_session(session_id, session)
    
    # Save to tmp for output
    with open('/tmp/combat_state.json', 'w') as f:
        json.dump(combat_state, f, indent=2)
    
    return combat_state


def next_turn(session_id, params):
    """Advance to the next turn."""
    combat_state = load_combat_state()
    if not combat_state or not combat_state.get('active'):
        return {"error": "No active combat"}
    
    session = load_session(session_id)
    
    # Advance turn
    combat_state['turn_index'] += 1
    if combat_state['turn_index'] >= len(combat_state['combatants']):
        combat_state['turn_index'] = 0
        combat_state['round'] += 1
    
    current = combat_state['combatants'][combat_state['turn_index']]
    
    save_combat_state(combat_state)
    
    # Log event
    if session:
        event = create_event(
            "custom", "gm", current['id'],
            {"action": "next_turn", "round": combat_state['round']},
            {"current_turn": current['name']}
        )
        session['events'].append(event)
        save_session(session_id, session)
    
    with open('/tmp/combat_state.json', 'w') as f:
        json.dump(combat_state, f, indent=2)
    
    return combat_state


def end_combat(session_id, params):
    """End the current combat."""
    combat_state = load_combat_state()
    session = load_session(session_id)
    
    result = {
        "combat_ended": True,
        "total_rounds": combat_state.get('round', 0) if combat_state else 0
    }
    
    clear_combat_state()
    
    if session:
        event = create_event(
            "custom", "gm", None,
            {"action": "end_combat"},
            result
        )
        session['events'].append(event)
        save_session(session_id, session)
    
    with open('/tmp/combat_state.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    return result


def add_combatant(session_id, combatants, params):
    """Add combatants to active combat."""
    combat_state = load_combat_state()
    if not combat_state or not combat_state.get('active'):
        return {"error": "No active combat"}
    
    for char_id in combatants:
        char = load_character(char_id)
        if char:
            init = roll_initiative(char)
            combat_state['combatants'].append({
                "id": char_id,
                "name": char.get('name', char_id),
                "initiative": init,
                "hp": char.get('hp', {}).get('current', 0),
                "max_hp": char.get('hp', {}).get('max', 0)
            })
    
    # Re-sort by initiative
    combat_state['combatants'].sort(key=lambda x: x['initiative'], reverse=True)
    save_combat_state(combat_state)
    
    with open('/tmp/combat_state.json', 'w') as f:
        json.dump(combat_state, f, indent=2)
    
    return combat_state


def remove_combatant(session_id, target_id, params):
    """Remove a combatant from active combat."""
    combat_state = load_combat_state()
    if not combat_state or not combat_state.get('active'):
        return {"error": "No active combat"}
    
    combat_state['combatants'] = [
        c for c in combat_state['combatants'] if c['id'] != target_id
    ]
    
    # Adjust turn index if needed
    if combat_state['turn_index'] >= len(combat_state['combatants']):
        combat_state['turn_index'] = 0
    
    save_combat_state(combat_state)
    
    with open('/tmp/combat_state.json', 'w') as f:
        json.dump(combat_state, f, indent=2)
    
    return combat_state


def apply_damage_combat(session_id, target_id, amount, params):
    """Apply damage to a combatant."""
    combat_state = load_combat_state()
    session = load_session(session_id)
    
    char = load_character(target_id)
    if char:
        old_hp = char.get('hp', {}).get('current', 0)
        new_hp = max(0, old_hp - amount)
        char['hp']['current'] = new_hp
        save_character(target_id, char)
        
        # Update combat state
        if combat_state:
            for c in combat_state['combatants']:
                if c['id'] == target_id:
                    c['hp'] = new_hp
            save_combat_state(combat_state)
        
        result = {
            "target": target_id,
            "old_hp": old_hp,
            "new_hp": new_hp,
            "damage": amount
        }
        
        if session:
            event = create_event("damage", "gm", target_id,
                               {"amount": amount}, result)
            session['events'].append(event)
            save_session(session_id, session)
        
        with open('/tmp/combat_state.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        return result
    
    return {"error": f"Character '{target_id}' not found"}


def apply_healing_combat(session_id, target_id, amount, params):
    """Apply healing to a combatant."""
    combat_state = load_combat_state()
    session = load_session(session_id)
    
    char = load_character(target_id)
    if char:
        old_hp = char.get('hp', {}).get('current', 0)
        max_hp = char.get('hp', {}).get('max', old_hp)
        new_hp = min(max_hp, old_hp + amount)
        char['hp']['current'] = new_hp
        save_character(target_id, char)
        
        # Update combat state
        if combat_state:
            for c in combat_state['combatants']:
                if c['id'] == target_id:
                    c['hp'] = new_hp
            save_combat_state(combat_state)
        
        result = {
            "target": target_id,
            "old_hp": old_hp,
            "new_hp": new_hp,
            "healed": new_hp - old_hp
        }
        
        if session:
            event = create_event("heal", "gm", target_id,
                               {"amount": amount}, result)
            session['events'].append(event)
            save_session(session_id, session)
        
        with open('/tmp/combat_state.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        return result
    
    return {"error": f"Character '{target_id}' not found"}


def roll_initiative_all(session_id, combatants, params):
    """Re-roll initiative for specified combatants."""
    combat_state = load_combat_state()
    if not combat_state or not combat_state.get('active'):
        return {"error": "No active combat"}
    
    for char_id in combatants:
        char = load_character(char_id)
        if char:
            init = roll_initiative(char)
            for c in combat_state['combatants']:
                if c['id'] == char_id:
                    c['initiative'] = init
    
    # Re-sort
    combat_state['combatants'].sort(key=lambda x: x['initiative'], reverse=True)
    save_combat_state(combat_state)
    
    with open('/tmp/combat_state.json', 'w') as f:
        json.dump(combat_state, f, indent=2)
    
    return combat_state


def get_combat_state_action(session_id, params):
    """Get current combat state."""
    combat_state = load_combat_state()
    
    if not combat_state:
        result = {"active": False, "message": "No active combat"}
    else:
        result = combat_state
    
    with open('/tmp/combat_state.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Combat manager')
    parser.add_argument('--action', required=True,
                       choices=['start_combat', 'next_turn', 'end_combat',
                               'add_combatant', 'remove_combatant',
                               'apply_damage', 'apply_healing',
                               'roll_initiative', 'get_combat_state'])
    parser.add_argument('--session', required=True, help='Session ID')
    parser.add_argument('--combatants', default='', help='Comma-separated character IDs')
    parser.add_argument('--target', default='', help='Target character ID')
    parser.add_argument('--amount', type=int, default=0, help='Amount for damage/healing')
    parser.add_argument('--params-file', help='Path to JSON params file')
    
    args = parser.parse_args()
    
    combatants = [c.strip() for c in args.combatants.split(',') if c.strip()]
    
    params = {}
    if args.params_file and os.path.exists(args.params_file):
        with open(args.params_file, 'r') as f:
            params = json.load(f)
    
    handlers = {
        'start_combat': lambda: start_combat(args.session, combatants, params),
        'next_turn': lambda: next_turn(args.session, params),
        'end_combat': lambda: end_combat(args.session, params),
        'add_combatant': lambda: add_combatant(args.session, combatants, params),
        'remove_combatant': lambda: remove_combatant(args.session, args.target, params),
        'apply_damage': lambda: apply_damage_combat(args.session, args.target, args.amount, params),
        'apply_healing': lambda: apply_healing_combat(args.session, args.target, args.amount, params),
        'roll_initiative': lambda: roll_initiative_all(args.session, combatants, params),
        'get_combat_state': lambda: get_combat_state_action(args.session, params)
    }
    
    result = handlers[args.action]()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

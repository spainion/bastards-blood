#!/usr/bin/env python3
"""Agent tasks for AI-powered game assistance."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def load_character(char_id):
    """Load a character file."""
    path = f"data/characters/{char_id}.json"
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None


def load_all_characters():
    """Load all character files."""
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


def load_session(session_id):
    """Load a session file."""
    path = f"data/sessions/{session_id}.json"
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None


def load_all_sessions():
    """Load all session files."""
    sessions = {}
    sessions_dir = "data/sessions"
    if os.path.exists(sessions_dir):
        for filename in os.listdir(sessions_dir):
            if filename.endswith('.json'):
                with open(os.path.join(sessions_dir, filename), 'r') as f:
                    sess = json.load(f)
                    if 'id' in sess:
                        sessions[sess['id']] = sess
    return sessions


def analyze_character(targets, context):
    """Analyze character stats and provide insights."""
    results = []
    
    for char_id in targets:
        char = load_character(char_id)
        if not char:
            results.append({"id": char_id, "error": "Character not found"})
            continue
        
        stats = char.get('stats', {})
        hp = char.get('hp', {})
        
        # Calculate stat modifiers
        modifiers = {}
        for stat, value in stats.items():
            modifiers[stat] = (value - 10) // 2
        
        # Identify strengths and weaknesses
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        strengths = [s[0] for s in sorted_stats[:2]]
        weaknesses = [s[0] for s in sorted_stats[-2:]]
        
        # HP analysis
        hp_percent = (hp.get('current', 0) / hp.get('max', 1)) * 100 if hp.get('max', 0) > 0 else 0
        hp_status = "healthy" if hp_percent > 75 else "injured" if hp_percent > 25 else "critical"
        
        analysis = {
            "id": char_id,
            "name": char.get('name'),
            "class": char.get('class'),
            "level": char.get('lvl'),
            "stat_modifiers": modifiers,
            "primary_strengths": strengths,
            "weaknesses": weaknesses,
            "hp_status": hp_status,
            "hp_percent": round(hp_percent, 1),
            "combat_role": determine_combat_role(stats, char.get('class', '')),
            "recommendations": generate_recommendations(char, modifiers)
        }
        results.append(analysis)
    
    return {"task": "analyze_character", "results": results}


def determine_combat_role(stats, char_class):
    """Determine combat role based on stats and class."""
    str_val = stats.get('STR', 10)
    dex_val = stats.get('DEX', 10)
    con_val = stats.get('CON', 10)
    int_val = stats.get('INT', 10)
    wis_val = stats.get('WIS', 10)
    cha_val = stats.get('CHA', 10)
    
    if str_val >= 14 and con_val >= 12:
        return "frontline_melee"
    elif dex_val >= 14:
        return "ranged_striker"
    elif int_val >= 14 or wis_val >= 14:
        return "spellcaster"
    elif cha_val >= 14:
        return "face_support"
    else:
        return "balanced"


def generate_recommendations(char, modifiers):
    """Generate tactical recommendations for a character."""
    recommendations = []
    
    # Based on class
    char_class = char.get('class', '').lower()
    if 'rogue' in char_class:
        recommendations.append("Use Sneak Attack when you have advantage")
        recommendations.append("Position for flanking opportunities")
    elif 'fighter' in char_class or 'warrior' in char_class:
        recommendations.append("Engage high-threat enemies to protect allies")
        recommendations.append("Use Action Surge for critical moments")
    elif 'mage' in char_class or 'wizard' in char_class:
        recommendations.append("Maintain distance from melee threats")
        recommendations.append("Save high-level slots for emergencies")
    
    # Based on HP
    hp = char.get('hp', {})
    hp_percent = (hp.get('current', 0) / hp.get('max', 1)) * 100 if hp.get('max', 0) > 0 else 0
    if hp_percent < 50:
        recommendations.append("Consider healing or defensive actions")
    
    return recommendations


def suggest_encounter(targets, context):
    """Suggest encounter ideas based on party composition."""
    characters = [load_character(t) for t in targets if load_character(t)]
    
    if not characters:
        return {"task": "suggest_encounter", "error": "No valid characters found"}
    
    # Calculate party stats
    avg_level = sum(c.get('lvl', 1) for c in characters) / len(characters)
    party_size = len(characters)
    
    # Determine party composition
    roles = [determine_combat_role(c.get('stats', {}), c.get('class', '')) for c in characters]
    has_healer = any('support' in r for r in roles)
    has_tank = any('frontline' in r for r in roles)
    
    suggestions = []
    
    # Suggest based on party composition
    if has_tank and has_healer:
        suggestions.append({
            "type": "boss_battle",
            "description": "Party is well-balanced for a challenging boss encounter",
            "recommended_cr": avg_level + 2,
            "enemies": ["Single powerful enemy with legendary actions"]
        })
    
    if party_size >= 4:
        suggestions.append({
            "type": "horde",
            "description": "Large party can handle multiple weaker enemies",
            "recommended_cr": avg_level - 2,
            "enemy_count": party_size * 2,
            "enemies": ["Swarm of lesser enemies"]
        })
    
    suggestions.append({
        "type": "balanced",
        "description": "Standard encounter for the party",
        "recommended_cr": avg_level,
        "enemy_count": party_size,
        "enemies": ["Mix of enemy types matching party level"]
    })
    
    return {
        "task": "suggest_encounter",
        "party_analysis": {
            "size": party_size,
            "average_level": round(avg_level, 1),
            "roles": roles,
            "has_healer": has_healer,
            "has_tank": has_tank
        },
        "suggestions": suggestions
    }


def generate_loot(targets, context):
    """Generate loot suggestions."""
    difficulty = context.get('difficulty', 'medium')
    loot_type = context.get('loot_type', 'mixed')
    
    loot_tables = {
        "easy": {
            "gold_range": [10, 50],
            "item_chance": 0.3,
            "magic_chance": 0.05
        },
        "medium": {
            "gold_range": [50, 200],
            "item_chance": 0.5,
            "magic_chance": 0.15
        },
        "hard": {
            "gold_range": [200, 500],
            "item_chance": 0.7,
            "magic_chance": 0.3
        },
        "deadly": {
            "gold_range": [500, 2000],
            "item_chance": 0.9,
            "magic_chance": 0.5
        }
    }
    
    table = loot_tables.get(difficulty, loot_tables["medium"])
    
    import random
    gold = random.randint(*table["gold_range"])
    
    items = []
    if random.random() < table["item_chance"]:
        mundane_items = ["healing potion", "rope", "torch", "rations", "lockpicks", 
                        "antitoxin", "holy water", "oil flask"]
        items.append(random.choice(mundane_items))
    
    if random.random() < table["magic_chance"]:
        magic_items = ["Potion of Healing", "+1 Weapon", "Ring of Protection",
                      "Cloak of Elvenkind", "Bag of Holding", "Wand of Magic Missiles"]
        items.append(random.choice(magic_items))
    
    return {
        "task": "generate_loot",
        "difficulty": difficulty,
        "loot": {
            "gold": gold,
            "items": items
        }
    }


def session_recap(targets, context):
    """Generate a session recap from events."""
    results = []
    
    for session_id in targets:
        session = load_session(session_id)
        if not session:
            results.append({"session_id": session_id, "error": "Session not found"})
            continue
        
        events = session.get('events', [])
        
        # Categorize events
        combat_events = [e for e in events if e.get('t') in ('attack', 'damage', 'heal')]
        narrative_events = [e for e in events if e.get('t') == 'note']
        item_events = [e for e in events if e.get('t') in ('gain_item', 'lose_item')]
        
        # Extract key moments
        key_moments = []
        for event in events:
            if event.get('t') == 'note':
                data = event.get('data', {})
                if data.get('narrative_type') in ('plot_point', 'discovery', 'chapter_end'):
                    key_moments.append(data.get('text', '')[:200])
        
        recap = {
            "session_id": session_id,
            "campaign": session.get('campaign'),
            "total_events": len(events),
            "combat_events": len(combat_events),
            "narrative_events": len(narrative_events),
            "items_gained": len([e for e in item_events if e.get('t') == 'gain_item']),
            "items_lost": len([e for e in item_events if e.get('t') == 'lose_item']),
            "key_moments": key_moments[:5]
        }
        results.append(recap)
    
    return {"task": "session_recap", "results": results}


def story_hook(targets, context):
    """Generate story hooks based on characters and context."""
    characters = [load_character(t) for t in targets if load_character(t)]
    
    hooks = []
    
    for char in characters:
        char_hooks = []
        notes = char.get('notes', '').lower()
        tags = char.get('tags', [])
        
        # Generate hooks based on character traits
        if 'mysterious' in notes or 'unknown' in notes:
            char_hooks.append(f"A figure from {char['name']}'s past appears with urgent news")
        
        if 'party' in tags:
            char_hooks.append(f"{char['name']} receives a letter from their homeland")
        
        # Class-based hooks
        char_class = char.get('class', '').lower()
        if 'rogue' in char_class:
            char_hooks.append(f"An old contact offers {char['name']} a lucrative heist")
        elif 'cleric' in char_class or 'paladin' in char_class:
            char_hooks.append(f"{char['name']}'s deity sends a divine vision")
        
        hooks.append({
            "character": char['name'],
            "hooks": char_hooks if char_hooks else ["A personal quest awaits"]
        })
    
    # General party hooks
    party_hooks = [
        "A desperate villager seeks help against a local threat",
        "A mysterious map fragment is discovered",
        "An old enemy resurfaces with new allies",
        "A lucrative bounty is posted for a dangerous creature"
    ]
    
    return {
        "task": "story_hook",
        "character_hooks": hooks,
        "party_hooks": party_hooks
    }


def main():
    parser = argparse.ArgumentParser(description='Agent tasks')
    parser.add_argument('--task', required=True,
                       choices=['analyze_character', 'suggest_encounter', 'generate_loot',
                               'balance_check', 'story_hook', 'npc_dialogue',
                               'location_description', 'combat_summary', 'session_recap',
                               'character_development'])
    parser.add_argument('--targets', default='', help='Comma-separated target IDs')
    parser.add_argument('--context-file', help='Path to JSON context file')
    parser.add_argument('--output-file', default='/tmp/task_result.json')
    
    args = parser.parse_args()
    
    targets = [t.strip() for t in args.targets.split(',') if t.strip()]
    
    context = {}
    if args.context_file and os.path.exists(args.context_file):
        with open(args.context_file, 'r') as f:
            context = json.load(f)
    
    handlers = {
        'analyze_character': lambda: analyze_character(targets, context),
        'suggest_encounter': lambda: suggest_encounter(targets, context),
        'generate_loot': lambda: generate_loot(targets, context),
        'story_hook': lambda: story_hook(targets, context),
        'session_recap': lambda: session_recap(targets, context),
        'balance_check': lambda: {"task": "balance_check", "message": "Not yet implemented"},
        'npc_dialogue': lambda: {"task": "npc_dialogue", "message": "Not yet implemented"},
        'location_description': lambda: {"task": "location_description", "message": "Not yet implemented"},
        'combat_summary': lambda: {"task": "combat_summary", "message": "Not yet implemented"},
        'character_development': lambda: {"task": "character_development", "message": "Not yet implemented"}
    }
    
    result = handlers[args.task]()
    
    with open(args.output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

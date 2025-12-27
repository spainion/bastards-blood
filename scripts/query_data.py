#!/usr/bin/env python3
"""Query game data with various filters and options."""

import argparse
import json
import os
import sys
from datetime import datetime


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


def load_world_data():
    """Load world data if available."""
    world_dir = "data/world"
    world = {}
    if os.path.exists(world_dir):
        for subdir in ['locations', 'items', 'quests', 'factions']:
            subpath = os.path.join(world_dir, subdir)
            if os.path.exists(subpath):
                world[subdir] = {}
                for filename in os.listdir(subpath):
                    if filename.endswith('.json'):
                        with open(os.path.join(subpath, filename), 'r') as f:
                            data = json.load(f)
                            if 'id' in data:
                                world[subdir][data['id']] = data
    return world


def query_all_characters(limit):
    """Get all characters."""
    chars = load_all_characters()
    result = list(chars.values())[:limit]
    return {"count": len(result), "characters": result}


def query_all_sessions(limit):
    """Get all sessions."""
    sessions = load_all_sessions()
    result = sorted(sessions.values(), key=lambda s: s.get('id', ''), reverse=True)[:limit]
    return {"count": len(result), "sessions": result}


def query_character_by_id(resource_id):
    """Get a specific character."""
    chars = load_all_characters()
    char = chars.get(resource_id)
    if char:
        return {"found": True, "character": char}
    return {"found": False, "error": f"Character '{resource_id}' not found"}


def query_session_by_id(resource_id):
    """Get a specific session."""
    sessions = load_all_sessions()
    sess = sessions.get(resource_id)
    if sess:
        return {"found": True, "session": sess}
    return {"found": False, "error": f"Session '{resource_id}' not found"}


def query_characters_by_tag(filter_value, limit):
    """Get characters with a specific tag."""
    chars = load_all_characters()
    result = [c for c in chars.values() if filter_value in c.get('tags', [])][:limit]
    return {"count": len(result), "tag": filter_value, "characters": result}


def query_game_state(resource_id):
    """Get computed game state for a session."""
    from get_game_state import load_all_characters, load_session, reduce, generate_summary
    
    state = {"characters": load_all_characters()}
    if resource_id:
        session = load_session(resource_id)
        for event in session.get("events", []):
            state = reduce(state, event)
    
    return generate_summary(state)


def query_recent_events(limit):
    """Get recent events across all sessions."""
    sessions = load_all_sessions()
    all_events = []
    
    for sess_id, sess in sessions.items():
        for event in sess.get('events', []):
            event_copy = event.copy()
            event_copy['session_id'] = sess_id
            all_events.append(event_copy)
    
    # Sort by timestamp descending
    all_events.sort(key=lambda e: e.get('ts', ''), reverse=True)
    result = all_events[:limit]
    
    return {"count": len(result), "events": result}


def query_search(filter_value, limit):
    """Search across all data."""
    results = {
        "query": filter_value,
        "characters": [],
        "sessions": [],
        "events": []
    }
    
    search_term = filter_value.lower()
    
    # Search characters
    chars = load_all_characters()
    for char in chars.values():
        if (search_term in char.get('name', '').lower() or
            search_term in char.get('notes', '').lower() or
            search_term in char.get('class', '').lower()):
            results['characters'].append(char)
    
    # Search sessions
    sessions = load_all_sessions()
    for sess in sessions.values():
        if search_term in sess.get('campaign', '').lower():
            results['sessions'].append(sess)
        
        # Search events
        for event in sess.get('events', []):
            data_str = json.dumps(event.get('data', {})).lower()
            if search_term in data_str:
                event_copy = event.copy()
                event_copy['session_id'] = sess['id']
                results['events'].append(event_copy)
    
    # Apply limits
    results['characters'] = results['characters'][:limit]
    results['sessions'] = results['sessions'][:limit]
    results['events'] = results['events'][:limit]
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Query game data')
    parser.add_argument('--query-type', required=True,
                       choices=['all_characters', 'all_sessions', 'character_by_id',
                               'session_by_id', 'characters_by_tag', 'game_state',
                               'recent_events', 'search'])
    parser.add_argument('--resource-id', default='')
    parser.add_argument('--filter', default='')
    parser.add_argument('--limit', type=int, default=50)
    parser.add_argument('--output-file', default='/tmp/query_result.json')
    
    args = parser.parse_args()
    
    handlers = {
        'all_characters': lambda: query_all_characters(args.limit),
        'all_sessions': lambda: query_all_sessions(args.limit),
        'character_by_id': lambda: query_character_by_id(args.resource_id),
        'session_by_id': lambda: query_session_by_id(args.resource_id),
        'characters_by_tag': lambda: query_characters_by_tag(args.filter, args.limit),
        'game_state': lambda: query_game_state(args.resource_id),
        'recent_events': lambda: query_recent_events(args.limit),
        'search': lambda: query_search(args.filter, args.limit)
    }
    
    result = handlers[args.query_type]()
    
    with open(args.output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

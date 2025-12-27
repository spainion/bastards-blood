#!/usr/bin/env python3
"""Log narrative entries to game sessions."""

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


def log_narrative(session_id, narrative_type, text, characters, location, mood):
    """Log a narrative entry to a session."""
    session = load_session(session_id)
    if not session:
        raise ValueError(f"Session not found: {session_id}")
    
    event_data = {
        "narrative_type": narrative_type,
        "text": text
    }
    
    if characters:
        event_data["characters_involved"] = characters
    if location:
        event_data["location"] = location
    if mood:
        event_data["mood"] = mood
    
    event = {
        "id": generate_event_id(),
        "ts": datetime.now(timezone.utc).isoformat(),
        "t": "note",
        "actor": "gm",
        "data": event_data
    }
    
    session['events'].append(event)
    save_session(session_id, session)
    
    return event


def main():
    parser = argparse.ArgumentParser(description='Log narrative entry')
    parser.add_argument('--session', required=True, help='Session ID')
    parser.add_argument('--type', required=True, dest='narrative_type',
                       choices=['scene_description', 'dialogue', 'action_description',
                               'combat_narration', 'discovery', 'rest_scene',
                               'travel_description', 'npc_interaction', 'plot_point',
                               'chapter_end'])
    parser.add_argument('--text-file', help='Path to file containing narrative text')
    parser.add_argument('--characters', default='', help='Comma-separated character IDs')
    parser.add_argument('--location', default='', help='Current location')
    parser.add_argument('--mood', default='', help='Scene mood/atmosphere')
    
    args = parser.parse_args()
    
    # Load narrative text from file
    text = ""
    if args.text_file and os.path.exists(args.text_file):
        with open(args.text_file, 'r') as f:
            text = f.read().strip()
    
    characters = [c.strip() for c in args.characters.split(',') if c.strip()]
    
    event = log_narrative(
        args.session,
        args.narrative_type,
        text,
        characters,
        args.location,
        args.mood
    )
    
    print(f"Logged narrative event: {event['id']}")
    print(json.dumps(event, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

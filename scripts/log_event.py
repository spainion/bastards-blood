#!/usr/bin/env python3
"""Log a game event to a session."""

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


def create_event(
    event_type: str,
    actor: str = None,
    target: str = None,
    data: dict = None,
    result: dict = None
) -> dict:
    """Create an event dictionary."""
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


def main():
    parser = argparse.ArgumentParser(description='Log a game event to a session')
    parser.add_argument('--session', required=True, help='Session ID')
    parser.add_argument('--type', required=True, dest='event_type',
                       choices=['note', 'check', 'attack', 'damage', 'heal',
                               'gain_item', 'lose_item', 'status', 'create_char',
                               'update_char', 'custom'],
                       help='Event type')
    parser.add_argument('--actor', default='', help='Actor character ID')
    parser.add_argument('--target', default='', help='Target character ID')
    parser.add_argument('--data-file', help='Path to JSON file containing event data')
    parser.add_argument('--result-file', help='Path to JSON file containing event result')
    
    args = parser.parse_args()
    
    # Load event data and result from files
    data = {}
    result = {}
    
    if args.data_file and os.path.exists(args.data_file):
        with open(args.data_file, 'r') as f:
            content = f.read().strip()
            if content:
                data = json.loads(content)
    
    if args.result_file and os.path.exists(args.result_file):
        with open(args.result_file, 'r') as f:
            content = f.read().strip()
            if content:
                result = json.loads(content)
    
    # Load session
    session = load_session(args.session)
    
    # Create event
    event = create_event(
        event_type=args.event_type,
        actor=args.actor if args.actor else None,
        target=args.target if args.target else None,
        data=data if data else None,
        result=result if result else None
    )
    
    # Append event to session
    session['events'].append(event)
    
    # Save session
    save_session(args.session, session)
    
    print(f"Logged event {event['id']} to session {args.session}")
    print(json.dumps(event, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

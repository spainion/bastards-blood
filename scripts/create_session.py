#!/usr/bin/env python3
"""Create a new game session."""

import argparse
import json
import os
import sys
from datetime import datetime


def get_next_session_number(date_str: str) -> int:
    """Get the next session number for a given date."""
    sessions_dir = "data/sessions"
    prefix = f"{date_str}-"
    
    if not os.path.exists(sessions_dir):
        return 1
    
    max_num = 0
    for filename in os.listdir(sessions_dir):
        if filename.startswith(prefix) and filename.endswith('.json'):
            try:
                num_str = filename[len(prefix):-5]  # Remove prefix and .json
                num = int(num_str)
                max_num = max(max_num, num)
            except ValueError:
                continue
    
    return max_num + 1


def create_session(campaign: str, date_str: str) -> str:
    """Create a new session and return its ID."""
    session_num = get_next_session_number(date_str)
    session_id = f"{date_str}-{session_num:04d}"
    
    session = {
        "id": session_id,
        "campaign": campaign,
        "events": []
    }
    
    # Write to file
    output_path = f"data/sessions/{session_id}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(session, f, indent=2)
    
    return session_id


def main():
    parser = argparse.ArgumentParser(description='Create a new game session')
    parser.add_argument('--campaign', default='bastards-blood', help='Campaign name')
    parser.add_argument('--date', default=None, help='Session date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Default to today if no date provided
    date_str = args.date if args.date else datetime.now().strftime('%Y-%m-%d')
    
    session_id = create_session(args.campaign, date_str)
    print(session_id)
    return 0


if __name__ == '__main__':
    sys.exit(main())

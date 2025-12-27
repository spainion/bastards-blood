#!/usr/bin/env python3
"""Data sync and export utilities."""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone


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
    """Load all world data."""
    world = {}
    world_dir = "data/world"
    if os.path.exists(world_dir):
        for subdir in os.listdir(world_dir):
            subpath = os.path.join(world_dir, subdir)
            if os.path.isdir(subpath):
                world[subdir] = {}
                for filename in os.listdir(subpath):
                    if filename.endswith('.json'):
                        with open(os.path.join(subpath, filename), 'r') as f:
                            data = json.load(f)
                            if 'id' in data:
                                world[subdir][data['id']] = data
    return world


def export_to_json(data, output_path):
    """Export data to JSON format."""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


def export_to_yaml(data, output_path):
    """Export data to YAML format."""
    try:
        import yaml
        with open(output_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    except ImportError:
        # Fallback to JSON if yaml not available
        export_to_json(data, output_path.replace('.yaml', '.json'))


def export_to_markdown(data, output_path, data_type):
    """Export data to Markdown format."""
    with open(output_path, 'w') as f:
        f.write(f"# {data_type.title()} Export\n\n")
        f.write(f"*Exported at: {datetime.now(timezone.utc).isoformat()}*\n\n")
        
        if isinstance(data, dict):
            for key, value in data.items():
                f.write(f"## {key}\n\n")
                if isinstance(value, dict):
                    f.write("```json\n")
                    f.write(json.dumps(value, indent=2))
                    f.write("\n```\n\n")
                else:
                    f.write(f"{value}\n\n")


def export_all(fmt, include_computed):
    """Export all game data."""
    os.makedirs('/tmp/export', exist_ok=True)
    
    data = {
        "characters": load_all_characters(),
        "sessions": load_all_sessions(),
        "world": load_world_data(),
        "exported_at": datetime.now(timezone.utc).isoformat()
    }
    
    if include_computed:
        # Add computed game state
        from get_game_state import reduce, generate_summary
        state = {"characters": data["characters"].copy()}
        
        # Apply all session events
        for sess in data["sessions"].values():
            for event in sess.get("events", []):
                state = reduce(state, event)
        
        data["computed_state"] = generate_summary(state)
    
    if fmt == 'json':
        export_to_json(data, '/tmp/export/all_data.json')
    elif fmt == 'yaml':
        export_to_yaml(data, '/tmp/export/all_data.yaml')
    else:
        export_to_markdown(data, '/tmp/export/all_data.md', 'all_data')
    
    return {"exported": True, "format": fmt}


def export_characters(fmt, include_computed):
    """Export character data."""
    os.makedirs('/tmp/export', exist_ok=True)
    
    data = load_all_characters()
    
    if fmt == 'json':
        export_to_json(data, '/tmp/export/characters.json')
    elif fmt == 'yaml':
        export_to_yaml(data, '/tmp/export/characters.yaml')
    else:
        export_to_markdown(data, '/tmp/export/characters.md', 'characters')
    
    return {"exported": True, "count": len(data), "format": fmt}


def export_sessions(fmt, include_computed):
    """Export session data."""
    os.makedirs('/tmp/export', exist_ok=True)
    
    data = load_all_sessions()
    
    if fmt == 'json':
        export_to_json(data, '/tmp/export/sessions.json')
    elif fmt == 'yaml':
        export_to_yaml(data, '/tmp/export/sessions.yaml')
    else:
        export_to_markdown(data, '/tmp/export/sessions.md', 'sessions')
    
    return {"exported": True, "count": len(data), "format": fmt}


def export_world(fmt, include_computed):
    """Export world data."""
    os.makedirs('/tmp/export', exist_ok=True)
    
    data = load_world_data()
    
    if fmt == 'json':
        export_to_json(data, '/tmp/export/world.json')
    elif fmt == 'yaml':
        export_to_yaml(data, '/tmp/export/world.yaml')
    else:
        export_to_markdown(data, '/tmp/export/world.md', 'world')
    
    return {"exported": True, "categories": list(data.keys()), "format": fmt}


def backup_all():
    """Create a backup of all data."""
    os.makedirs('/tmp/export', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'/tmp/export/backup_{timestamp}'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copy data directories
    if os.path.exists('data'):
        shutil.copytree('data', os.path.join(backup_dir, 'data'))
    
    # Copy schemas
    if os.path.exists('schemas'):
        shutil.copytree('schemas', os.path.join(backup_dir, 'schemas'))
    
    # Create manifest
    manifest = {
        "backup_time": datetime.now(timezone.utc).isoformat(),
        "characters": len(load_all_characters()),
        "sessions": len(load_all_sessions())
    }
    
    with open(os.path.join(backup_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return {"backed_up": True, "path": backup_dir, "manifest": manifest}


def validate_all():
    """Validate all data files (placeholder - actual validation done in workflow)."""
    return {"action": "validate_all", "message": "Validation performed by workflow"}


def main():
    parser = argparse.ArgumentParser(description='Data sync utilities')
    parser.add_argument('--action', required=True,
                       choices=['export_all', 'export_characters', 'export_sessions',
                               'export_world', 'import_data', 'validate_all',
                               'backup', 'restore'])
    parser.add_argument('--format', choices=['json', 'yaml', 'markdown'], default='json')
    parser.add_argument('--include-computed', default='true')
    
    args = parser.parse_args()
    
    include_computed = args.include_computed.lower() == 'true'
    
    handlers = {
        'export_all': lambda: export_all(args.format, include_computed),
        'export_characters': lambda: export_characters(args.format, include_computed),
        'export_sessions': lambda: export_sessions(args.format, include_computed),
        'export_world': lambda: export_world(args.format, include_computed),
        'backup': backup_all,
        'validate_all': validate_all,
        'import_data': lambda: {"action": "import_data", "message": "Import not yet implemented"},
        'restore': lambda: {"action": "restore", "message": "Restore not yet implemented"}
    }
    
    result = handlers[args.action]()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

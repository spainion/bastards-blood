#!/usr/bin/env python3
"""World building tools for creating game content."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def ensure_world_dirs():
    """Ensure world data directories exist."""
    dirs = [
        "data/world",
        "data/world/locations",
        "data/world/items",
        "data/world/quests",
        "data/world/factions",
        "data/world/npcs"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def save_entity(entity_type, entity_id, data):
    """Save a world entity to file."""
    ensure_world_dirs()
    
    type_to_dir = {
        'location': 'locations',
        'item': 'items',
        'quest': 'quests',
        'faction': 'factions',
        'npc': 'npcs'
    }
    
    subdir = type_to_dir.get(entity_type, entity_type + 's')
    path = f"data/world/{subdir}/{entity_id}.json"
    
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return path


def load_entity(entity_type, entity_id):
    """Load a world entity from file."""
    type_to_dir = {
        'location': 'locations',
        'item': 'items',
        'quest': 'quests',
        'faction': 'factions',
        'npc': 'npcs'
    }
    
    subdir = type_to_dir.get(entity_type, entity_type + 's')
    path = f"data/world/{subdir}/{entity_id}.json"
    
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None


def create_location(entity_id, data):
    """Create a new location."""
    location = {
        "id": entity_id,
        "type": "location",
        "name": data.get('name', entity_id),
        "description": data.get('description', ''),
        "region": data.get('region', ''),
        "terrain": data.get('terrain', 'unknown'),
        "notable_features": data.get('notable_features', []),
        "connections": data.get('connections', []),
        "npcs_present": data.get('npcs_present', []),
        "encounters": data.get('encounters', []),
        "loot": data.get('loot', []),
        "notes": data.get('notes', ''),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    path = save_entity('location', entity_id, location)
    return {"created": True, "path": path, "entity": location}


def create_npc(entity_id, data):
    """Create a new NPC."""
    npc = {
        "id": entity_id,
        "type": "npc",
        "name": data.get('name', entity_id),
        "role": data.get('role', 'commoner'),
        "description": data.get('description', ''),
        "personality": data.get('personality', ''),
        "location": data.get('location', ''),
        "faction": data.get('faction', ''),
        "attitude": data.get('attitude', 'neutral'),
        "services": data.get('services', []),
        "inventory": data.get('inventory', []),
        "dialogue_hooks": data.get('dialogue_hooks', []),
        "secrets": data.get('secrets', []),
        "notes": data.get('notes', ''),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    path = save_entity('npc', entity_id, npc)
    return {"created": True, "path": path, "entity": npc}


def create_item(entity_id, data):
    """Create a new item."""
    item = {
        "id": entity_id,
        "type": "item",
        "name": data.get('name', entity_id),
        "item_type": data.get('item_type', 'miscellaneous'),
        "rarity": data.get('rarity', 'common'),
        "description": data.get('description', ''),
        "properties": data.get('properties', []),
        "value": data.get('value', 0),
        "weight": data.get('weight', 0),
        "attunement": data.get('attunement', False),
        "effects": data.get('effects', []),
        "notes": data.get('notes', ''),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    path = save_entity('item', entity_id, item)
    return {"created": True, "path": path, "entity": item}


def create_quest(entity_id, data):
    """Create a new quest."""
    quest = {
        "id": entity_id,
        "type": "quest",
        "name": data.get('name', entity_id),
        "quest_type": data.get('quest_type', 'main'),
        "status": data.get('status', 'available'),
        "giver": data.get('giver', ''),
        "description": data.get('description', ''),
        "objectives": data.get('objectives', []),
        "rewards": data.get('rewards', []),
        "prerequisites": data.get('prerequisites', []),
        "location": data.get('location', ''),
        "difficulty": data.get('difficulty', 'medium'),
        "notes": data.get('notes', ''),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    path = save_entity('quest', entity_id, quest)
    return {"created": True, "path": path, "entity": quest}


def create_faction(entity_id, data):
    """Create a new faction."""
    faction = {
        "id": entity_id,
        "type": "faction",
        "name": data.get('name', entity_id),
        "description": data.get('description', ''),
        "alignment": data.get('alignment', 'neutral'),
        "leader": data.get('leader', ''),
        "headquarters": data.get('headquarters', ''),
        "goals": data.get('goals', []),
        "allies": data.get('allies', []),
        "enemies": data.get('enemies', []),
        "members": data.get('members', []),
        "resources": data.get('resources', []),
        "reputation": data.get('reputation', 0),
        "notes": data.get('notes', ''),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    path = save_entity('faction', entity_id, faction)
    return {"created": True, "path": path, "entity": faction}


def update_world_state(entity_type, entity_id, data):
    """Update an existing world entity."""
    entity = load_entity(entity_type, entity_id)
    if not entity:
        return {"error": f"Entity not found: {entity_type}/{entity_id}"}
    
    # Update with new data
    for key, value in data.items():
        if key not in ('id', 'type', 'created_at'):
            entity[key] = value
    
    entity['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    path = save_entity(entity_type, entity_id, entity)
    return {"updated": True, "path": path, "entity": entity}


def get_world_data(entity_type, entity_id):
    """Get world data."""
    if entity_id:
        entity = load_entity(entity_type, entity_id)
        return {"found": entity is not None, "entity": entity}
    
    # List all entities of type
    ensure_world_dirs()
    type_to_dir = {
        'location': 'locations',
        'item': 'items',
        'quest': 'quests',
        'faction': 'factions',
        'npc': 'npcs'
    }
    
    subdir = type_to_dir.get(entity_type, entity_type + 's')
    dir_path = f"data/world/{subdir}"
    
    entities = []
    if os.path.exists(dir_path):
        for filename in os.listdir(dir_path):
            if filename.endswith('.json'):
                with open(os.path.join(dir_path, filename), 'r') as f:
                    entities.append(json.load(f))
    
    return {"count": len(entities), "entities": entities}


def main():
    parser = argparse.ArgumentParser(description='World builder')
    parser.add_argument('--action', required=True,
                       choices=['create_location', 'create_npc', 'create_item',
                               'create_quest', 'create_faction', 'update_world_state',
                               'get_world_data'])
    parser.add_argument('--entity-type', default='')
    parser.add_argument('--entity-id', default='')
    parser.add_argument('--data-file', help='Path to JSON data file')
    
    args = parser.parse_args()
    
    data = {}
    if args.data_file and os.path.exists(args.data_file):
        with open(args.data_file, 'r') as f:
            data = json.load(f)
    
    handlers = {
        'create_location': lambda: create_location(args.entity_id, data),
        'create_npc': lambda: create_npc(args.entity_id, data),
        'create_item': lambda: create_item(args.entity_id, data),
        'create_quest': lambda: create_quest(args.entity_id, data),
        'create_faction': lambda: create_faction(args.entity_id, data),
        'update_world_state': lambda: update_world_state(args.entity_type, args.entity_id, data),
        'get_world_data': lambda: get_world_data(args.entity_type, args.entity_id)
    }
    
    result = handlers[args.action]()
    
    with open('/tmp/world_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

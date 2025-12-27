#!/usr/bin/env python3
"""Context engine for building optimized LLM context windows."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional


def estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation: ~4 chars per token)."""
    return len(text) // 4


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


def load_memories(category: Optional[str] = None, limit: int = 20):
    """Load relevant memories."""
    index_path = "data/memory/_index/index.json"
    if not os.path.exists(index_path):
        return []
    
    with open(index_path, 'r') as f:
        index = json.load(f)
    
    memories = []
    candidate_ids = list(index.get("memories", {}).keys())
    
    if category:
        candidate_ids = [
            mid for mid in candidate_ids
            if index["memories"][mid].get("category") == category
        ]
    
    # Sort by importance
    candidate_ids.sort(
        key=lambda x: index["memories"][x].get("importance", 0),
        reverse=True
    )
    
    for memory_id in candidate_ids[:limit]:
        memory_info = index["memories"][memory_id]
        cat = memory_info["category"]
        memory_path = f"data/memory/{cat}/{memory_id}.json"
        
        if os.path.exists(memory_path):
            with open(memory_path, 'r') as f:
                memories.append(json.load(f))
    
    return memories


def load_world_data():
    """Load world data."""
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


def get_recent_events(sessions: dict, count: int = 20) -> list:
    """Get the most recent events across all sessions."""
    all_events = []
    
    for sess_id, sess in sessions.items():
        for event in sess.get('events', []):
            event_copy = event.copy()
            event_copy['session_id'] = sess_id
            all_events.append(event_copy)
    
    # Sort by timestamp descending
    all_events.sort(key=lambda e: e.get('ts', ''), reverse=True)
    return all_events[:count]


def build_full_game_state(max_tokens: int, include_memories: bool, recent_events: int) -> dict:
    """Build complete game state context."""
    context = {
        "type": "full_game_state",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": []
    }
    
    characters = load_all_characters()
    sessions = load_all_sessions()
    
    # Characters section
    char_section = {
        "name": "Characters",
        "data": list(characters.values())
    }
    context["sections"].append(char_section)
    
    # Recent events section
    if recent_events > 0:
        events = get_recent_events(sessions, recent_events)
        events_section = {
            "name": "Recent Events",
            "data": events
        }
        context["sections"].append(events_section)
    
    # Memories section
    if include_memories:
        memories = load_memories(limit=10)
        if memories:
            memory_section = {
                "name": "Relevant Memories",
                "data": [{"content": m.get("content"), "category": m.get("category")} for m in memories]
            }
            context["sections"].append(memory_section)
    
    # Estimate and truncate if needed
    context_str = json.dumps(context)
    tokens = estimate_tokens(context_str)
    context["estimated_tokens"] = tokens
    context["within_limit"] = tokens <= max_tokens
    
    return context


def build_character_focused(focus_ids: list, max_tokens: int, include_memories: bool, recent_events: int) -> dict:
    """Build character-focused context."""
    context = {
        "type": "character_focused",
        "focus_characters": focus_ids,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": []
    }
    
    characters = load_all_characters()
    sessions = load_all_sessions()
    
    # Focused characters (full detail)
    focused_chars = [characters[cid] for cid in focus_ids if cid in characters]
    context["sections"].append({
        "name": "Focus Characters",
        "data": focused_chars
    })
    
    # Other characters (summary only)
    other_chars = [
        {"id": c["id"], "name": c.get("name"), "class": c.get("class"), "lvl": c.get("lvl")}
        for cid, c in characters.items() if cid not in focus_ids
    ]
    if other_chars:
        context["sections"].append({
            "name": "Other Characters (Summary)",
            "data": other_chars
        })
    
    # Events involving focus characters
    if recent_events > 0:
        all_events = get_recent_events(sessions, recent_events * 2)
        relevant_events = [
            e for e in all_events
            if e.get("actor") in focus_ids or e.get("target") in focus_ids
        ][:recent_events]
        
        if relevant_events:
            context["sections"].append({
                "name": "Character Events",
                "data": relevant_events
            })
    
    # Character-related memories
    if include_memories:
        memories = load_memories(category="character_knowledge", limit=5)
        if memories:
            context["sections"].append({
                "name": "Character Memories",
                "data": [m.get("content") for m in memories]
            })
    
    context["estimated_tokens"] = estimate_tokens(json.dumps(context))
    return context


def build_session_focused(focus_ids: list, max_tokens: int, include_memories: bool, recent_events: int) -> dict:
    """Build session-focused context."""
    context = {
        "type": "session_focused",
        "focus_sessions": focus_ids,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": []
    }
    
    sessions = load_all_sessions()
    characters = load_all_characters()
    
    # Focus session details
    for sess_id in focus_ids:
        if sess_id in sessions:
            sess = sessions[sess_id]
            context["sections"].append({
                "name": f"Session: {sess_id}",
                "data": sess
            })
    
    # Character summaries
    char_summaries = [
        {"id": c["id"], "name": c.get("name"), "hp": c.get("hp")}
        for c in characters.values()
    ]
    context["sections"].append({
        "name": "Character Status",
        "data": char_summaries
    })
    
    # Session-related memories
    if include_memories:
        memories = load_memories(category="session_history", limit=5)
        if memories:
            context["sections"].append({
                "name": "Session Memories",
                "data": [m.get("content") for m in memories]
            })
    
    context["estimated_tokens"] = estimate_tokens(json.dumps(context))
    return context


def build_combat_focused(focus_ids: list, max_tokens: int, include_memories: bool, recent_events: int) -> dict:
    """Build combat-focused context."""
    context = {
        "type": "combat_focused",
        "combatants": focus_ids,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": []
    }
    
    characters = load_all_characters()
    
    # Combat-relevant character data
    combatants = []
    for cid in focus_ids:
        if cid in characters:
            char = characters[cid]
            combatants.append({
                "id": char["id"],
                "name": char.get("name"),
                "class": char.get("class"),
                "lvl": char.get("lvl"),
                "stats": char.get("stats"),
                "hp": char.get("hp"),
                "inventory": char.get("inventory", [])[:5]  # Limited inventory
            })
    
    context["sections"].append({
        "name": "Combatants",
        "data": combatants
    })
    
    # Load combat state if exists
    combat_state_path = "data/combat_state.json"
    if os.path.exists(combat_state_path):
        with open(combat_state_path, 'r') as f:
            combat_state = json.load(f)
        context["sections"].append({
            "name": "Combat State",
            "data": combat_state
        })
    
    context["estimated_tokens"] = estimate_tokens(json.dumps(context))
    return context


def build_narrative_focused(focus_ids: list, max_tokens: int, include_memories: bool, recent_events: int) -> dict:
    """Build narrative-focused context."""
    context = {
        "type": "narrative_focused",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": []
    }
    
    sessions = load_all_sessions()
    
    # Extract narrative events
    all_events = []
    for sess_id, sess in sessions.items():
        for event in sess.get('events', []):
            if event.get('t') == 'note':
                event_copy = event.copy()
                event_copy['session_id'] = sess_id
                all_events.append(event_copy)
    
    all_events.sort(key=lambda e: e.get('ts', ''), reverse=True)
    narrative_events = all_events[:recent_events]
    
    context["sections"].append({
        "name": "Narrative History",
        "data": [e.get("data", {}).get("text", "") for e in narrative_events if e.get("data")]
    })
    
    # Plot-related memories
    if include_memories:
        memories = load_memories(category="plot_threads", limit=10)
        if memories:
            context["sections"].append({
                "name": "Plot Threads",
                "data": [m.get("content") for m in memories]
            })
    
    context["estimated_tokens"] = estimate_tokens(json.dumps(context))
    return context


def build_world_focused(focus_ids: list, max_tokens: int, include_memories: bool, recent_events: int) -> dict:
    """Build world-focused context."""
    context = {
        "type": "world_focused",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": []
    }
    
    world = load_world_data()
    
    for category, entities in world.items():
        if focus_ids:
            # Filter to focused entities
            filtered = {k: v for k, v in entities.items() if k in focus_ids}
            if filtered:
                context["sections"].append({
                    "name": category.title(),
                    "data": list(filtered.values())
                })
        else:
            # Include all (summarized)
            summaries = [
                {"id": e.get("id"), "name": e.get("name"), "type": e.get("type")}
                for e in entities.values()
            ]
            if summaries:
                context["sections"].append({
                    "name": category.title(),
                    "data": summaries
                })
    
    # World lore memories
    if include_memories:
        memories = load_memories(category="world_lore", limit=10)
        if memories:
            context["sections"].append({
                "name": "World Lore",
                "data": [m.get("content") for m in memories]
            })
    
    context["estimated_tokens"] = estimate_tokens(json.dumps(context))
    return context


def summarize_context(context: dict, target_tokens: int) -> dict:
    """Summarize context to fit within token limit."""
    # This is a simplified version - a real implementation would use
    # more sophisticated summarization
    summarized = {
        "type": f"{context.get('type', 'unknown')}_summarized",
        "original_type": context.get("type"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": []
    }
    
    for section in context.get("sections", []):
        data = section.get("data", [])
        if isinstance(data, list) and len(data) > 5:
            # Truncate lists
            summarized["sections"].append({
                "name": section["name"],
                "data": data[:5],
                "truncated": True,
                "original_count": len(data)
            })
        else:
            summarized["sections"].append(section)
    
    summarized["estimated_tokens"] = estimate_tokens(json.dumps(summarized))
    summarized["target_tokens"] = target_tokens
    
    return summarized


def compress_context(context: dict) -> dict:
    """Compress context by removing redundant information."""
    compressed = {
        "type": f"{context.get('type', 'unknown')}_compressed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data": {}
    }
    
    # Flatten and deduplicate
    for section in context.get("sections", []):
        name = section.get("name", "unknown")
        data = section.get("data", [])
        
        if isinstance(data, list):
            # Keep only essential fields
            compressed["data"][name] = len(data)
        else:
            compressed["data"][name] = "present"
    
    compressed["estimated_tokens"] = estimate_tokens(json.dumps(compressed))
    return compressed


def main():
    parser = argparse.ArgumentParser(description='Context engine')
    parser.add_argument('--action', required=True,
                       choices=['build_context', 'get_relevant_context', 'summarize_context',
                               'compress_context', 'merge_contexts', 'export_context'])
    parser.add_argument('--context-type', default='full_game_state',
                       choices=['full_game_state', 'character_focused', 'session_focused',
                               'combat_focused', 'narrative_focused', 'world_focused'])
    parser.add_argument('--focus-ids', default='')
    parser.add_argument('--max-tokens', type=int, default=4000)
    parser.add_argument('--include-memories', default='true')
    parser.add_argument('--include-recent-events', type=int, default=20)
    parser.add_argument('--params-file', help='Path to params JSON file')
    
    args = parser.parse_args()
    
    focus_ids = [fid.strip() for fid in args.focus_ids.split(',') if fid.strip()]
    include_memories = args.include_memories.lower() == 'true'
    
    context_builders = {
        'full_game_state': build_full_game_state,
        'character_focused': build_character_focused,
        'session_focused': build_session_focused,
        'combat_focused': build_combat_focused,
        'narrative_focused': build_narrative_focused,
        'world_focused': build_world_focused
    }
    
    if args.action == 'build_context' or args.action == 'get_relevant_context':
        builder = context_builders.get(args.context_type, build_full_game_state)
        if args.context_type in ('full_game_state',):
            result = builder(args.max_tokens, include_memories, args.include_recent_events)
        else:
            result = builder(focus_ids, args.max_tokens, include_memories, args.include_recent_events)
    elif args.action == 'summarize_context':
        # Load existing context and summarize
        context = context_builders['full_game_state'](args.max_tokens, include_memories, args.include_recent_events)
        result = summarize_context(context, args.max_tokens // 2)
    elif args.action == 'compress_context':
        context = context_builders['full_game_state'](args.max_tokens, include_memories, args.include_recent_events)
        result = compress_context(context)
    else:
        result = {"action": args.action, "message": "Action not fully implemented"}
    
    with open('/tmp/context_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Persistent memory store for GPT context management."""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional


def ensure_memory_dirs():
    """Ensure memory directories exist."""
    dirs = [
        "data/memory",
        "data/memory/character_knowledge",
        "data/memory/world_lore",
        "data/memory/session_history",
        "data/memory/player_preferences",
        "data/memory/plot_threads",
        "data/memory/npc_relationships",
        "data/memory/item_catalog",
        "data/memory/rules_clarifications",
        "data/memory/custom",
        "data/memory/_index"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def generate_memory_id(content: str) -> str:
    """Generate a unique memory ID based on content hash."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"mem_{timestamp}_{content_hash}"


def load_memory_index() -> dict:
    """Load the memory index."""
    index_path = "data/memory/_index/index.json"
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return json.load(f)
    return {
        "memories": {},
        "categories": {},
        "tags": {},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }


def save_memory_index(index: dict):
    """Save the memory index."""
    ensure_memory_dirs()
    index["updated_at"] = datetime.now(timezone.utc).isoformat()
    index_path = "data/memory/_index/index.json"
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)


def store_memory(category: str, content: dict, tags: list, importance: int) -> dict:
    """Store a new memory."""
    ensure_memory_dirs()
    
    content_str = json.dumps(content)
    memory_id = generate_memory_id(content_str)
    
    memory = {
        "id": memory_id,
        "category": category,
        "content": content,
        "tags": tags,
        "importance": importance,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "access_count": 0,
        "last_accessed": None
    }
    
    # Save memory file
    memory_path = f"data/memory/{category}/{memory_id}.json"
    with open(memory_path, 'w') as f:
        json.dump(memory, f, indent=2)
    
    # Update index
    index = load_memory_index()
    index["memories"][memory_id] = {
        "category": category,
        "importance": importance,
        "tags": tags,
        "created_at": memory["created_at"]
    }
    
    # Update category index
    if category not in index["categories"]:
        index["categories"][category] = []
    index["categories"][category].append(memory_id)
    
    # Update tag index
    for tag in tags:
        if tag not in index["tags"]:
            index["tags"][tag] = []
        index["tags"][tag].append(memory_id)
    
    save_memory_index(index)
    
    return {"stored": True, "memory_id": memory_id, "memory": memory}


def retrieve_memory(memory_id: str) -> dict:
    """Retrieve a specific memory by ID."""
    index = load_memory_index()
    
    if memory_id not in index["memories"]:
        return {"found": False, "error": f"Memory not found: {memory_id}"}
    
    category = index["memories"][memory_id]["category"]
    memory_path = f"data/memory/{category}/{memory_id}.json"
    
    if not os.path.exists(memory_path):
        return {"found": False, "error": f"Memory file not found: {memory_path}"}
    
    with open(memory_path, 'r') as f:
        memory = json.load(f)
    
    # Update access stats
    memory["access_count"] += 1
    memory["last_accessed"] = datetime.now(timezone.utc).isoformat()
    with open(memory_path, 'w') as f:
        json.dump(memory, f, indent=2)
    
    return {"found": True, "memory": memory}


def search_memories(query: str, category: Optional[str], tags: list, limit: int) -> dict:
    """Search memories by content, category, or tags."""
    index = load_memory_index()
    results = []
    
    # Get candidate memory IDs
    candidate_ids = set(index["memories"].keys())
    
    # Filter by category
    if category:
        category_ids = set(index["categories"].get(category, []))
        candidate_ids &= category_ids
    
    # Filter by tags (any match)
    if tags:
        tag_ids = set()
        for tag in tags:
            tag_ids.update(index["tags"].get(tag, []))
        candidate_ids &= tag_ids
    
    # Search content
    for memory_id in candidate_ids:
        memory_info = index["memories"][memory_id]
        cat = memory_info["category"]
        memory_path = f"data/memory/{cat}/{memory_id}.json"
        
        if os.path.exists(memory_path):
            with open(memory_path, 'r') as f:
                memory = json.load(f)
            
            # Simple text search
            content_str = json.dumps(memory.get("content", {})).lower()
            if not query or query.lower() in content_str:
                results.append({
                    "id": memory_id,
                    "category": cat,
                    "importance": memory.get("importance", 5),
                    "tags": memory.get("tags", []),
                    "content_preview": str(memory.get("content", {}))[:200],
                    "created_at": memory.get("created_at")
                })
    
    # Sort by importance descending
    results.sort(key=lambda x: x["importance"], reverse=True)
    results = results[:limit]
    
    return {"query": query, "count": len(results), "results": results}


def update_memory(memory_id: str, content: dict, tags: list, importance: int) -> dict:
    """Update an existing memory."""
    index = load_memory_index()
    
    if memory_id not in index["memories"]:
        return {"updated": False, "error": f"Memory not found: {memory_id}"}
    
    category = index["memories"][memory_id]["category"]
    memory_path = f"data/memory/{category}/{memory_id}.json"
    
    if not os.path.exists(memory_path):
        return {"updated": False, "error": f"Memory file not found"}
    
    with open(memory_path, 'r') as f:
        memory = json.load(f)
    
    # Update fields
    if content:
        memory["content"] = content
    if tags:
        memory["tags"] = tags
    if importance:
        memory["importance"] = importance
    memory["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    with open(memory_path, 'w') as f:
        json.dump(memory, f, indent=2)
    
    # Update index
    index["memories"][memory_id]["importance"] = memory["importance"]
    index["memories"][memory_id]["tags"] = memory["tags"]
    save_memory_index(index)
    
    return {"updated": True, "memory": memory}


def delete_memory(memory_id: str) -> dict:
    """Delete a memory."""
    index = load_memory_index()
    
    if memory_id not in index["memories"]:
        return {"deleted": False, "error": f"Memory not found: {memory_id}"}
    
    memory_info = index["memories"][memory_id]
    category = memory_info["category"]
    memory_path = f"data/memory/{category}/{memory_id}.json"
    
    # Delete file
    if os.path.exists(memory_path):
        os.remove(memory_path)
    
    # Update index
    del index["memories"][memory_id]
    
    if category in index["categories"]:
        index["categories"][category] = [
            mid for mid in index["categories"][category] if mid != memory_id
        ]
    
    for tag in memory_info.get("tags", []):
        if tag in index["tags"]:
            index["tags"][tag] = [
                mid for mid in index["tags"][tag] if mid != memory_id
            ]
    
    save_memory_index(index)
    
    return {"deleted": True, "memory_id": memory_id}


def list_categories() -> dict:
    """List all memory categories and counts."""
    index = load_memory_index()
    
    categories = {}
    for cat, memory_ids in index.get("categories", {}).items():
        categories[cat] = len(memory_ids)
    
    tags = {}
    for tag, memory_ids in index.get("tags", {}).items():
        tags[tag] = len(memory_ids)
    
    return {
        "total_memories": len(index.get("memories", {})),
        "categories": categories,
        "tags": tags
    }


def get_context(category: Optional[str], tags: list, limit: int) -> dict:
    """Get relevant memories for context building."""
    index = load_memory_index()
    memories = []
    
    candidate_ids = set(index["memories"].keys())
    
    if category:
        candidate_ids &= set(index["categories"].get(category, []))
    
    if tags:
        tag_ids = set()
        for tag in tags:
            tag_ids.update(index["tags"].get(tag, []))
        candidate_ids &= tag_ids
    
    # Load and sort memories
    for memory_id in candidate_ids:
        memory_info = index["memories"][memory_id]
        cat = memory_info["category"]
        memory_path = f"data/memory/{cat}/{memory_id}.json"
        
        if os.path.exists(memory_path):
            with open(memory_path, 'r') as f:
                memory = json.load(f)
            memories.append(memory)
    
    # Sort by importance, then by recency
    memories.sort(key=lambda x: (x.get("importance", 0), x.get("created_at", "")), reverse=True)
    memories = memories[:limit]
    
    # Format for context
    context_items = []
    for mem in memories:
        context_items.append({
            "id": mem["id"],
            "category": mem["category"],
            "content": mem["content"],
            "importance": mem["importance"]
        })
    
    return {"count": len(context_items), "context": context_items}


def prune_memories(max_age_days: int = 90, min_importance: int = 3) -> dict:
    """Prune old, low-importance memories."""
    index = load_memory_index()
    pruned = []
    
    cutoff_date = datetime.now(timezone.utc)
    
    for memory_id, memory_info in list(index["memories"].items()):
        # Skip high importance memories
        if memory_info.get("importance", 5) >= min_importance:
            continue
        
        category = memory_info["category"]
        memory_path = f"data/memory/{category}/{memory_id}.json"
        
        if os.path.exists(memory_path):
            with open(memory_path, 'r') as f:
                memory = json.load(f)
            
            created_str = memory.get("created_at", "")
            if created_str:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                age_days = (cutoff_date - created).days
                
                if age_days > max_age_days:
                    delete_memory(memory_id)
                    pruned.append(memory_id)
    
    return {"pruned": len(pruned), "memory_ids": pruned}


def main():
    parser = argparse.ArgumentParser(description='Memory store operations')
    parser.add_argument('--operation', required=True,
                       choices=['store', 'retrieve', 'search', 'update', 'delete',
                               'list_categories', 'get_context', 'prune'])
    parser.add_argument('--memory-id', default='')
    parser.add_argument('--category', default='custom')
    parser.add_argument('--tags', default='')
    parser.add_argument('--search-query', default='')
    parser.add_argument('--importance', type=int, default=5)
    parser.add_argument('--context-limit', type=int, default=20)
    parser.add_argument('--content-file', help='Path to content JSON file')
    
    args = parser.parse_args()
    
    tags = [t.strip() for t in args.tags.split(',') if t.strip()]
    
    content = {}
    if args.content_file and os.path.exists(args.content_file):
        with open(args.content_file, 'r') as f:
            try:
                content = json.load(f)
            except json.JSONDecodeError:
                content = {"text": f.read()}
    
    handlers = {
        'store': lambda: store_memory(args.category, content, tags, args.importance),
        'retrieve': lambda: retrieve_memory(args.memory_id),
        'search': lambda: search_memories(args.search_query, args.category if args.category != 'custom' else None, tags, args.context_limit),
        'update': lambda: update_memory(args.memory_id, content, tags, args.importance),
        'delete': lambda: delete_memory(args.memory_id),
        'list_categories': list_categories,
        'get_context': lambda: get_context(args.category if args.category != 'custom' else None, tags, args.context_limit),
        'prune': lambda: prune_memories()
    }
    
    result = handlers[args.operation]()
    
    with open('/tmp/memory_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

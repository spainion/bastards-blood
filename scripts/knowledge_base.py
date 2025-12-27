#!/usr/bin/env python3
"""Knowledge base for semantic search and document indexing."""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional


def ensure_knowledge_dirs():
    """Ensure knowledge base directories exist."""
    dirs = [
        "data/knowledge",
        "data/knowledge/documents",
        "data/knowledge/index"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def generate_doc_id(content: str) -> str:
    """Generate a document ID based on content hash."""
    content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
    return f"doc_{content_hash}"


def tokenize(text: str) -> list:
    """Simple tokenization for search."""
    import re
    # Convert to lowercase and split on non-alphanumeric
    tokens = re.findall(r'\b\w+\b', text.lower())
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                  'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                  'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                  'through', 'during', 'before', 'after', 'above', 'below',
                  'between', 'under', 'again', 'further', 'then', 'once',
                  'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either',
                  'neither', 'not', 'only', 'own', 'same', 'than', 'too',
                  'very', 'just', 'also'}
    return [t for t in tokens if t not in stop_words and len(t) > 2]


def load_index() -> dict:
    """Load the knowledge base index."""
    index_path = "data/knowledge/index/main.json"
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return json.load(f)
    return {
        "documents": {},
        "inverted_index": {},
        "doc_types": {},
        "statistics": {
            "total_documents": 0,
            "total_tokens": 0
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }


def save_index(index: dict):
    """Save the knowledge base index."""
    ensure_knowledge_dirs()
    index["updated_at"] = datetime.now(timezone.utc).isoformat()
    index_path = "data/knowledge/index/main.json"
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)


def add_document(doc_type: str, doc_id: str, content: str) -> dict:
    """Add a document to the knowledge base."""
    ensure_knowledge_dirs()
    
    if not doc_id:
        doc_id = generate_doc_id(content)
    
    # Tokenize content
    tokens = tokenize(content)
    token_freq = {}
    for token in tokens:
        token_freq[token] = token_freq.get(token, 0) + 1
    
    document = {
        "id": doc_id,
        "type": doc_type,
        "content": content,
        "tokens": token_freq,
        "token_count": len(tokens),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Save document
    doc_path = f"data/knowledge/documents/{doc_id}.json"
    with open(doc_path, 'w') as f:
        json.dump(document, f, indent=2)
    
    # Update index
    index = load_index()
    
    index["documents"][doc_id] = {
        "type": doc_type,
        "token_count": len(tokens),
        "created_at": document["created_at"]
    }
    
    # Update inverted index
    for token, freq in token_freq.items():
        if token not in index["inverted_index"]:
            index["inverted_index"][token] = {}
        index["inverted_index"][token][doc_id] = freq
    
    # Update type index
    if doc_type not in index["doc_types"]:
        index["doc_types"][doc_type] = []
    if doc_id not in index["doc_types"][doc_type]:
        index["doc_types"][doc_type].append(doc_id)
    
    # Update statistics
    index["statistics"]["total_documents"] = len(index["documents"])
    index["statistics"]["total_tokens"] = len(index["inverted_index"])
    
    save_index(index)
    
    return {"added": True, "document_id": doc_id, "token_count": len(tokens)}


def search_documents(query: str, doc_type: Optional[str], top_k: int, filters: dict) -> dict:
    """Search documents using TF-IDF-like scoring."""
    index = load_index()
    
    # Tokenize query
    query_tokens = tokenize(query)
    
    if not query_tokens:
        return {"query": query, "results": [], "message": "No valid search terms"}
    
    # Get candidate documents
    candidate_docs = set()
    for token in query_tokens:
        if token in index["inverted_index"]:
            candidate_docs.update(index["inverted_index"][token].keys())
    
    # Filter by type
    if doc_type:
        type_docs = set(index["doc_types"].get(doc_type, []))
        candidate_docs &= type_docs
    
    # Score documents
    scores = {}
    total_docs = index["statistics"]["total_documents"]
    
    for doc_id in candidate_docs:
        score = 0
        doc_info = index["documents"].get(doc_id, {})
        doc_token_count = doc_info.get("token_count", 1)
        
        for token in query_tokens:
            if token in index["inverted_index"]:
                token_docs = index["inverted_index"][token]
                if doc_id in token_docs:
                    # TF: term frequency in document
                    tf = token_docs[doc_id] / doc_token_count
                    # IDF: inverse document frequency
                    idf = 1 + (total_docs / len(token_docs)) if token_docs else 1
                    score += tf * idf
        
        scores[doc_id] = score
    
    # Sort by score
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    # Load document contents for results
    results = []
    for doc_id, score in sorted_docs:
        doc_path = f"data/knowledge/documents/{doc_id}.json"
        if os.path.exists(doc_path):
            with open(doc_path, 'r') as f:
                doc = json.load(f)
            results.append({
                "id": doc_id,
                "type": doc.get("type"),
                "score": round(score, 4),
                "content_preview": doc.get("content", "")[:300],
                "token_count": doc.get("token_count")
            })
    
    return {
        "query": query,
        "tokens": query_tokens,
        "results_count": len(results),
        "results": results
    }


def get_related(doc_id: str, top_k: int) -> dict:
    """Get documents related to a given document."""
    index = load_index()
    
    if doc_id not in index["documents"]:
        return {"error": f"Document not found: {doc_id}"}
    
    # Load source document
    doc_path = f"data/knowledge/documents/{doc_id}.json"
    if not os.path.exists(doc_path):
        return {"error": "Document file not found"}
    
    with open(doc_path, 'r') as f:
        source_doc = json.load(f)
    
    # Get top tokens from source document
    source_tokens = source_doc.get("tokens", {})
    top_tokens = sorted(source_tokens.items(), key=lambda x: x[1], reverse=True)[:20]
    
    # Find related documents
    related_scores = {}
    for token, freq in top_tokens:
        if token in index["inverted_index"]:
            for related_id, related_freq in index["inverted_index"][token].items():
                if related_id != doc_id:
                    related_scores[related_id] = related_scores.get(related_id, 0) + (freq * related_freq)
    
    # Sort and limit
    sorted_related = sorted(related_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    results = []
    for related_id, score in sorted_related:
        related_path = f"data/knowledge/documents/{related_id}.json"
        if os.path.exists(related_path):
            with open(related_path, 'r') as f:
                related_doc = json.load(f)
            results.append({
                "id": related_id,
                "type": related_doc.get("type"),
                "similarity_score": round(score, 4),
                "content_preview": related_doc.get("content", "")[:200]
            })
    
    return {
        "source_document": doc_id,
        "related_count": len(results),
        "related": results
    }


def index_all() -> dict:
    """Index all game data into the knowledge base."""
    ensure_knowledge_dirs()
    indexed = {"characters": 0, "sessions": 0, "world": 0, "memories": 0}
    
    # Index characters
    chars_dir = "data/characters"
    if os.path.exists(chars_dir):
        for filename in os.listdir(chars_dir):
            if filename.endswith('.json'):
                with open(os.path.join(chars_dir, filename), 'r') as f:
                    char = json.load(f)
                content = f"Character: {char.get('name', '')}. Class: {char.get('class', '')}. "
                content += f"Notes: {char.get('notes', '')}. Tags: {', '.join(char.get('tags', []))}."
                add_document("character", char.get('id', filename), content)
                indexed["characters"] += 1
    
    # Index sessions
    sessions_dir = "data/sessions"
    if os.path.exists(sessions_dir):
        for filename in os.listdir(sessions_dir):
            if filename.endswith('.json'):
                with open(os.path.join(sessions_dir, filename), 'r') as f:
                    sess = json.load(f)
                
                # Create content from events
                content_parts = [f"Session: {sess.get('id', '')}. Campaign: {sess.get('campaign', '')}."]
                for event in sess.get('events', [])[:50]:  # Limit events
                    event_data = event.get('data', {})
                    if isinstance(event_data, dict):
                        content_parts.append(json.dumps(event_data))
                
                content = " ".join(content_parts)
                add_document("session", sess.get('id', filename), content)
                indexed["sessions"] += 1
    
    # Index world data
    world_dir = "data/world"
    if os.path.exists(world_dir):
        for subdir in os.listdir(world_dir):
            subpath = os.path.join(world_dir, subdir)
            if os.path.isdir(subpath):
                for filename in os.listdir(subpath):
                    if filename.endswith('.json'):
                        with open(os.path.join(subpath, filename), 'r') as f:
                            entity = json.load(f)
                        content = json.dumps(entity)
                        add_document("world_lore", entity.get('id', filename), content)
                        indexed["world"] += 1
    
    # Index memories
    memory_index_path = "data/memory/_index/index.json"
    if os.path.exists(memory_index_path):
        with open(memory_index_path, 'r') as f:
            mem_index = json.load(f)
        
        for memory_id, memory_info in mem_index.get("memories", {}).items():
            cat = memory_info.get("category", "custom")
            memory_path = f"data/memory/{cat}/{memory_id}.json"
            if os.path.exists(memory_path):
                with open(memory_path, 'r') as f:
                    memory = json.load(f)
                content = json.dumps(memory.get("content", {}))
                add_document("memory", memory_id, content)
                indexed["memories"] += 1
    
    return {"indexed": True, "counts": indexed}


def get_statistics() -> dict:
    """Get knowledge base statistics."""
    index = load_index()
    
    type_counts = {}
    for doc_type, doc_ids in index.get("doc_types", {}).items():
        type_counts[doc_type] = len(doc_ids)
    
    return {
        "total_documents": index["statistics"]["total_documents"],
        "total_unique_tokens": index["statistics"]["total_tokens"],
        "documents_by_type": type_counts,
        "index_updated_at": index.get("updated_at")
    }


def export_index() -> dict:
    """Export the index for backup or analysis."""
    index = load_index()
    
    export_path = "/tmp/knowledge_export.json"
    with open(export_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    return {"exported": True, "path": export_path, "statistics": get_statistics()}


def rebuild_index() -> dict:
    """Rebuild the entire index from documents."""
    # Clear existing index
    index = {
        "documents": {},
        "inverted_index": {},
        "doc_types": {},
        "statistics": {
            "total_documents": 0,
            "total_tokens": 0
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    save_index(index)
    
    # Re-index all documents
    docs_dir = "data/knowledge/documents"
    rebuilt = 0
    
    if os.path.exists(docs_dir):
        for filename in os.listdir(docs_dir):
            if filename.endswith('.json'):
                with open(os.path.join(docs_dir, filename), 'r') as f:
                    doc = json.load(f)
                
                # Re-add to index
                add_document(doc.get("type", "unknown"), doc.get("id"), doc.get("content", ""))
                rebuilt += 1
    
    return {"rebuilt": True, "documents_processed": rebuilt}


def main():
    parser = argparse.ArgumentParser(description='Knowledge base operations')
    parser.add_argument('--action', required=True,
                       choices=['index_all', 'add_document', 'search', 'get_related',
                               'update_embeddings', 'get_statistics', 'export_index',
                               'rebuild_index'])
    parser.add_argument('--document-type', default='custom')
    parser.add_argument('--document-id', default='')
    parser.add_argument('--search-query', default='')
    parser.add_argument('--top-k', type=int, default=10)
    parser.add_argument('--content-file', help='Path to content file')
    parser.add_argument('--filters-file', help='Path to filters JSON file')
    
    args = parser.parse_args()
    
    content = ""
    if args.content_file and os.path.exists(args.content_file):
        with open(args.content_file, 'r') as f:
            content = f.read()
    
    filters = {}
    if args.filters_file and os.path.exists(args.filters_file):
        with open(args.filters_file, 'r') as f:
            try:
                filters = json.load(f)
            except json.JSONDecodeError:
                pass
    
    handlers = {
        'index_all': index_all,
        'add_document': lambda: add_document(args.document_type, args.document_id, content),
        'search': lambda: search_documents(args.search_query, args.document_type if args.document_type != 'custom' else None, args.top_k, filters),
        'get_related': lambda: get_related(args.document_id, args.top_k),
        'update_embeddings': lambda: {"action": "update_embeddings", "message": "Embeddings not implemented (would require ML model)"},
        'get_statistics': get_statistics,
        'export_index': export_index,
        'rebuild_index': rebuild_index
    }
    
    result = handlers[args.action]()
    
    with open('/tmp/knowledge_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())

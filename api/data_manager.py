"""Data management for RPG game state."""
import json
import os
import copy
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import hashlib
from .models import Character, Event, Session, EventType
from .config import settings


class DataManager:
    """Manages game data persistence and state reduction."""
    
    def __init__(self):
        self.data_path = Path(settings.data_path)
        self.schemas_path = Path(settings.schemas_path)
        self.characters_path = self.data_path / "characters"
        self.sessions_path = self.data_path / "sessions"
        self.campaigns_path = self.data_path / "campaigns"
        
        # Ensure directories exist
        self.characters_path.mkdir(parents=True, exist_ok=True)
        self.sessions_path.mkdir(parents=True, exist_ok=True)
        self.campaigns_path.mkdir(parents=True, exist_ok=True)
    
    def load_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Load a character from file."""
        char_file = self.characters_path / f"{character_id}.json"
        if not char_file.exists():
            return None
        
        with open(char_file, 'r') as f:
            return json.load(f)
    
    def save_character(self, character: Dict[str, Any]) -> None:
        """Save a character to file."""
        char_id = character.get('id')
        if not char_id:
            raise ValueError("Character must have an 'id' field")
        
        char_file = self.characters_path / f"{char_id}.json"
        with open(char_file, 'w') as f:
            json.dump(character, f, indent=2)
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a session from file."""
        session_file = self.sessions_path / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        with open(session_file, 'r') as f:
            return json.load(f)
    
    def save_session(self, session: Dict[str, Any]) -> None:
        """Save a session to file."""
        session_id = session.get('id')
        if not session_id:
            raise ValueError("Session must have an 'id' field")
        
        session_file = self.sessions_path / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
    
    def list_characters(self) -> List[str]:
        """List all character IDs."""
        return [f.stem for f in self.characters_path.glob("*.json")]
    
    def list_sessions(self) -> List[str]:
        """List all session IDs."""
        return [f.stem for f in self.sessions_path.glob("*.json")]
    
    def generate_event_id(self) -> str:
        """Generate a unique event ID."""
        # Generate random 8-character hex string
        random_str = os.urandom(4).hex()
        return f"e_{random_str}"
    
    def add_event_to_session(self, session_id: str, event: Dict[str, Any]) -> None:
        """Add an event to a session."""
        session = self.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Generate event ID if not present
        if 'id' not in event:
            event['id'] = self.generate_event_id()
        
        # Add timestamp if not present
        if 'ts' not in event:
            event['ts'] = datetime.now(timezone.utc).isoformat() + 'Z'
        
        session['events'].append(event)
        self.save_session(session)
    
    def reduce_state(self, session_id: str) -> Dict[str, Any]:
        """Reduce session events to current game state."""
        session = self.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        state = {"characters": {}}
        
        for ev in session.get('events', []):
            state = self._reduce_event(state, ev)
        
        return state
    
    def _reduce_event(self, state: Dict[str, Any], ev: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a single event to the state (event sourcing)."""
        s = copy.deepcopy(state)
        t = ev.get("t")
        d = ev.get("data", {})
        r = ev.get("result", {})
        
        if t == "create_char":
            c = d.get("character", {})
            if c and "id" in c:
                s["characters"][c["id"]] = c
        
        elif t == "update_char":
            cid = d.get("id")
            if cid and cid in s["characters"]:
                s["characters"][cid].update(d.get("patch", {}))
        
        elif t == "gain_item":
            cid = d.get("id")
            item = d.get("item")
            if cid and cid in s["characters"] and item:
                s["characters"][cid].setdefault("inventory", []).append(item)
        
        elif t == "lose_item":
            cid = d.get("id")
            item = d.get("item")
            if cid and cid in s["characters"] and item:
                inv = s["characters"][cid].get("inventory", [])
                if item in inv:
                    inv.remove(item)
        
        elif t == "damage":
            cid = d.get("id")
            amt = r.get("amount", d.get("amount", 0))
            if cid and cid in s["characters"]:
                current_hp = s["characters"][cid]["hp"]["current"]
                s["characters"][cid]["hp"]["current"] = max(0, current_hp - amt)
        
        elif t == "heal":
            cid = d.get("id")
            amt = r.get("amount", d.get("amount", 0))
            if cid and cid in s["characters"]:
                mx = s["characters"][cid]["hp"]["max"]
                current_hp = s["characters"][cid]["hp"]["current"]
                s["characters"][cid]["hp"]["current"] = min(mx, current_hp + amt)
        
        return s
    
    def create_session(self, session_id: str, campaign: str) -> Dict[str, Any]:
        """Create a new game session."""
        session = {
            "id": session_id,
            "campaign": campaign,
            "events": []
        }
        self.save_session(session)
        return session


# Singleton instance
data_manager = DataManager()

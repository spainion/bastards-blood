"""WebSocket endpoint for real-time gameplay."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
import json
import asyncio
from datetime import datetime, timezone

from .database import get_db, GameSession, User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time gameplay."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, str] = {}  # user_id -> connection_id
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: int):
        """Accept and store new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.user_connections[user_id] = connection_id
        logger.info(f"WebSocket connected: {connection_id} (user {user_id})")
    
    def disconnect(self, connection_id: str, user_id: int):
        """Remove WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            await websocket.send_json(message)
    
    async def send_to_user(self, message: dict, user_id: int):
        """Send message to specific user."""
        if user_id in self.user_connections:
            connection_id = self.user_connections[user_id]
            await self.send_personal_message(message, connection_id)
    
    async def broadcast(self, message: dict, exclude: List[str] = None):
        """Broadcast message to all connections except excluded."""
        exclude = exclude or []
        for connection_id, websocket in self.active_connections.items():
            if connection_id not in exclude:
                await websocket.send_json(message)
    
    async def broadcast_to_session(self, message: dict, session_id: str, exclude: List[str] = None):
        """Broadcast to all players in a session."""
        # Note: Would need session tracking to implement fully
        await self.broadcast(message, exclude)


manager = ConnectionManager()


@router.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str, user_id: int, session_id: str):
    """
    WebSocket endpoint for real-time gameplay.
    
    Handles real-time events like:
    - Player movement
    - Combat updates
    - Chat messages
    - NPC interactions
    - World state changes
    """
    await manager.connect(websocket, connection_id, user_id)
    
    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "connection_id": connection_id,
        "message": "Connected to real-time game server",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type")
            
            if msg_type == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            elif msg_type == "movement":
                # Broadcast movement to other players in session
                await manager.broadcast_to_session({
                    "type": "player_moved",
                    "user_id": user_id,
                    "location": message.get("location"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id, exclude=[connection_id])
            
            elif msg_type == "combat_action":
                # Broadcast combat action
                await manager.broadcast_to_session({
                    "type": "combat_update",
                    "attacker_id": message.get("attacker_id"),
                    "action": message.get("action"),
                    "result": message.get("result"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
            
            elif msg_type == "chat":
                # Broadcast chat message
                await manager.broadcast_to_session({
                    "type": "chat_message",
                    "user_id": user_id,
                    "message": message.get("message"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
            
            elif msg_type == "npc_interaction":
                # Notify of NPC interaction
                await manager.broadcast_to_session({
                    "type": "npc_interaction",
                    "user_id": user_id,
                    "npc_id": message.get("npc_id"),
                    "interaction_type": message.get("interaction_type"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id, exclude=[connection_id])
            
            else:
                # Echo unknown messages
                await websocket.send_json({
                    "type": "echo",
                    "original_message": message,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id, user_id)
        # Notify others of disconnect
        await manager.broadcast_to_session({
            "type": "player_disconnected",
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(connection_id, user_id)


# Helper function to send real-time updates from REST endpoints
async def send_realtime_update(update_type: str, data: dict, session_id: str = None, user_id: int = None):
    """
    Send real-time update to connected clients.
    
    Can be called from REST endpoints to push updates via WebSocket.
    """
    message = {
        "type": update_type,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if user_id:
        await manager.send_to_user(message, user_id)
    elif session_id:
        await manager.broadcast_to_session(message, session_id)
    else:
        await manager.broadcast(message)

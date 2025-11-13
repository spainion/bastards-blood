"""
Admin and Multiplayer Models

Pydantic models for admin dashboard, in-game editing,
and enhanced multiplayer features.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# ADMIN MODELS
# ============================================================================

class AdminAction(BaseModel):
    """Admin action request"""
    admin_user_id: int
    action_type: str  # spawn_entity, modify_character, teleport_player, etc.
    target_id: Optional[str] = None
    data: Dict[str, Any]
    reason: Optional[str] = None


class AdminSpawnEntity(BaseModel):
    """Spawn entity (enemy, NPC, item) via admin"""
    session_id: str
    entity_type: str  # enemy, npc, item
    template_id: str
    location: Dict[str, float]  # x, y, z
    quantity: int = 1
    custom_properties: Optional[Dict[str, Any]] = None


class AdminModifyCharacter(BaseModel):
    """Modify character stats/inventory via admin"""
    character_id: str
    modifications: Dict[str, Any]  # hp, stats, inventory, etc.
    notify_player: bool = True


class AdminTeleportPlayer(BaseModel):
    """Teleport player to location"""
    character_id: str
    destination: Dict[str, float]
    notify_player: bool = True


class AdminBroadcastMessage(BaseModel):
    """Send message to all players"""
    message: str
    message_type: str = "announcement"  # announcement, warning, info
    duration: int = 5  # seconds to display


class AdminKickPlayer(BaseModel):
    """Kick player from session"""
    user_id: int
    reason: str
    ban_duration: Optional[int] = None  # minutes, None = no ban


class AdminAuditLog(BaseModel):
    """Admin action audit log entry"""
    id: Optional[int] = None
    admin_user_id: int
    admin_username: str
    action_type: str
    target_id: Optional[str] = None
    action_data: Dict[str, Any]
    reason: Optional[str] = None
    timestamp: datetime
    session_id: Optional[str] = None


# ============================================================================
# PARTY/GROUP SYSTEM
# ============================================================================

class Party(BaseModel):
    """Player party/group"""
    id: str
    name: str
    leader_id: str
    member_ids: List[str]
    max_members: int = 4
    created_at: datetime
    session_id: str
    is_public: bool = False  # Can others request to join?
    shared_xp: bool = True
    shared_loot: bool = False


class PartyInvite(BaseModel):
    """Party invitation"""
    inviter_id: str
    invitee_id: str
    party_id: str
    expires_at: datetime


class PartyAction(BaseModel):
    """Party management action"""
    party_id: str
    action: str  # invite, kick, leave, transfer_leadership, disband
    actor_id: str
    target_id: Optional[str] = None


# ============================================================================
# PLAYER TRADING
# ============================================================================

class TradeOffer(BaseModel):
    """Player-to-player trade offer"""
    id: str
    initiator_id: str
    recipient_id: str
    session_id: str
    initiator_items: List[Dict[str, Any]]
    initiator_currency: Dict[str, int]
    recipient_items: List[Dict[str, Any]]
    recipient_currency: Dict[str, int]
    status: str  # pending, accepted, declined, completed, cancelled
    created_at: datetime
    expires_at: datetime


class TradeAction(BaseModel):
    """Trade action (accept, decline, modify)"""
    trade_id: str
    action: str  # accept, decline, modify, cancel
    actor_id: str
    modifications: Optional[Dict[str, Any]] = None


# ============================================================================
# SOCIAL FEATURES
# ============================================================================

class FriendRequest(BaseModel):
    """Friend request"""
    requester_id: int
    recipient_id: int
    status: str = "pending"  # pending, accepted, declined
    created_at: datetime


class FriendsList(BaseModel):
    """User's friends list"""
    user_id: int
    friend_ids: List[int]
    blocked_ids: List[int] = []


class PlayerMessage(BaseModel):
    """Private message between players"""
    sender_id: int
    recipient_id: int
    content: str
    timestamp: datetime
    is_read: bool = False


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

class MultiplayerSession(BaseModel):
    """Enhanced multiplayer session"""
    id: str
    name: str
    host_user_id: int
    campaign: str
    max_players: int = 10
    current_players: List[int] = []
    is_public: bool = False
    password_protected: bool = False
    status: str = "active"  # active, paused, ended
    created_at: datetime
    game_settings: Dict[str, Any] = {}


class SessionJoinRequest(BaseModel):
    """Request to join session"""
    session_id: str
    user_id: int
    password: Optional[str] = None


# ============================================================================
# ADMIN DASHBOARD STATS
# ============================================================================

class ServerStats(BaseModel):
    """Server statistics for admin dashboard"""
    total_users: int
    active_sessions: int
    online_players: int
    total_characters: int
    total_npcs: int
    total_enemies: int
    database_size: Optional[str] = None
    uptime_seconds: int
    websocket_connections: int


class SessionStats(BaseModel):
    """Statistics for a specific session"""
    session_id: str
    player_count: int
    npc_count: int
    enemy_count: int
    events_count: int
    duration_seconds: int
    top_players: List[Dict[str, Any]]

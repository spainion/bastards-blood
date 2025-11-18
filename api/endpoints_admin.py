"""
Admin Dashboard and Multiplayer Endpoints

Admin tools for in-game editing, server management,
and enhanced multiplayer features.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

from .auth import get_current_user, require_admin
from .database import get_db, User, DBCharacter, DBEnemy
from .models_admin import (
    AdminSpawnEntity, AdminModifyCharacter, AdminTeleportPlayer,
    AdminBroadcastMessage, AdminKickPlayer, AdminAuditLog,
    Party, PartyInvite, PartyAction,
    TradeOffer, TradeAction,
    FriendRequest, PlayerMessage,
    MultiplayerSession, SessionJoinRequest,
    ServerStats, SessionStats
)
from .data_manager import DataManager

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
social_router = APIRouter(prefix="/api/v1/social", tags=["social"])
multiplayer_router = APIRouter(prefix="/api/v1/multiplayer", tags=["multiplayer"])

logger = logging.getLogger(__name__)
data_manager = DataManager()

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@router.get("/stats", response_model=ServerStats)
async def get_server_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get server statistics (admin only)"""
    total_users = db.query(User).count()
    total_characters = db.query(DBCharacter).count()
    total_enemies = db.query(DBEnemy).count()
    
    # Get active sessions from data manager
    active_sessions = len(data_manager.sessions)
    
    stats = ServerStats(
        total_users=total_users,
        active_sessions=active_sessions,
        online_players=0,  # TODO: Track from WebSocket connections
        total_characters=total_characters,
        total_npcs=len(data_manager.npcs),
        total_enemies=total_enemies,
        uptime_seconds=0,  # TODO: Track server uptime
        websocket_connections=0  # TODO: Track from WebSocket manager
    )
    
    return stats


@router.post("/spawn-entity")
async def admin_spawn_entity(
    request: AdminSpawnEntity,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Spawn entities in game (admin only)"""
    logger.info(f"Admin {current_user.username} spawning {request.entity_type}: {request.template_id}")
    
    result = []
    
    if request.entity_type == "enemy":
        from .endpoints_combat import spawn_enemy
        from .models_combat import SpawnEnemyRequest
        
        spawn_req = SpawnEnemyRequest(
            session_id=request.session_id,
            enemy_template=request.template_id,
            location=request.location,
            quantity=request.quantity
        )
        enemies = await spawn_enemy(spawn_req, current_user, db)
        result = enemies["enemies"]
    
    elif request.entity_type == "npc":
        # Spawn NPC
        from .models_npc import NPC
        for i in range(request.quantity):
            npc_id = f"admin-npc-{request.template_id}-{i}"
            npc_data = {
                "id": npc_id,
                "name": f"{request.template_id}_{i}",
                "npc_type": request.template_id,
                "location": request.location,
                **(request.custom_properties or {})
            }
            npc = NPC(**npc_data)
            data_manager.save_npc(npc)
            result.append(npc_data)
    
    elif request.entity_type == "item":
        # Spawn item at location
        result = [{
            "id": f"admin-item-{request.template_id}-{i}",
            "template": request.template_id,
            "location": request.location
        } for i in range(request.quantity)]
    
    # Log admin action
    audit_log = AdminAuditLog(
        admin_user_id=current_user.id,
        admin_username=current_user.username,
        action_type=f"spawn_{request.entity_type}",
        action_data=request.dict(),
        timestamp=datetime.utcnow(),
        session_id=request.session_id
    )
    
    return {
        "success": True,
        "spawned": result,
        "count": len(result)
    }


@router.post("/modify-character")
async def admin_modify_character(
    request: AdminModifyCharacter,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Modify character properties (admin only)"""
    logger.info(f"Admin {current_user.username} modifying character: {request.character_id}")
    
    # Load character
    character_data = data_manager.load_character(request.character_id)
    if not character_data:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Apply modifications
    for key, value in request.modifications.items():
        if key in character_data:
            character_data[key] = value
    
    # Save character
    data_manager.save_character(request.character_id, character_data)
    
    # Log admin action
    audit_log = AdminAuditLog(
        admin_user_id=current_user.id,
        admin_username=current_user.username,
        action_type="modify_character",
        target_id=request.character_id,
        action_data=request.dict(),
        timestamp=datetime.utcnow()
    )
    
    return {
        "success": True,
        "character_id": request.character_id,
        "modifications": request.modifications
    }


@router.post("/teleport-player")
async def admin_teleport_player(
    request: AdminTeleportPlayer,
    current_user: User = Depends(require_admin)
):
    """Teleport player to location (admin only)"""
    logger.info(f"Admin {current_user.username} teleporting {request.character_id}")
    
    # Load character
    character_data = data_manager.load_character(request.character_id)
    if not character_data:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Update location
    if "location" not in character_data:
        character_data["location"] = {}
    character_data["location"].update(request.destination)
    
    # Save character
    data_manager.save_character(request.character_id, character_data)
    
    return {
        "success": True,
        "character_id": request.character_id,
        "new_location": request.destination
    }


@router.post("/broadcast")
async def admin_broadcast_message(
    request: AdminBroadcastMessage,
    current_user: User = Depends(require_admin)
):
    """Broadcast message to all players (admin only)"""
    logger.info(f"Admin {current_user.username} broadcasting: {request.message}")
    
    # TODO: Send via WebSocket to all connected clients
    broadcast_data = {
        "type": "admin_broadcast",
        "message_type": request.message_type,
        "message": request.message,
        "duration": request.duration,
        "from": current_user.username
    }
    
    return {
        "success": True,
        "broadcast": broadcast_data
    }


# ============================================================================
# PARTY/GROUP SYSTEM
# ============================================================================

@multiplayer_router.post("/party/create", response_model=Party)
async def create_party(
    name: str,
    session_id: str,
    max_members: int = 4,
    current_user: User = Depends(get_current_user)
):
    """Create a new party"""
    party = Party(
        id=f"party-{datetime.utcnow().timestamp()}",
        name=name,
        leader_id=str(current_user.id),
        member_ids=[str(current_user.id)],
        max_members=max_members,
        created_at=datetime.utcnow(),
        session_id=session_id
    )
    
    # TODO: Store in database or data manager
    
    return party


@multiplayer_router.post("/party/invite")
async def invite_to_party(
    party_id: str,
    invitee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Invite player to party"""
    # TODO: Create party invite and notify invitee
    
    invite = PartyInvite(
        inviter_id=str(current_user.id),
        invitee_id=invitee_id,
        party_id=party_id,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    
    return {"success": True, "invite": invite}


@multiplayer_router.post("/party/action")
async def party_action(
    action: PartyAction,
    current_user: User = Depends(get_current_user)
):
    """Perform party action (kick, leave, etc.)"""
    # TODO: Validate and execute party action
    
    return {"success": True, "action": action.action}


# ============================================================================
# PLAYER TRADING
# ============================================================================

@social_router.post("/trade/offer", response_model=TradeOffer)
async def create_trade_offer(
    recipient_id: str,
    session_id: str,
    initiator_items: List[Dict],
    initiator_currency: Dict[str, int],
    current_user: User = Depends(get_current_user)
):
    """Create trade offer to another player"""
    trade = TradeOffer(
        id=f"trade-{datetime.utcnow().timestamp()}",
        initiator_id=str(current_user.id),
        recipient_id=recipient_id,
        session_id=session_id,
        initiator_items=initiator_items,
        initiator_currency=initiator_currency,
        recipient_items=[],
        recipient_currency={},
        status="pending",
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    
    # TODO: Store and notify recipient
    
    return trade


@social_router.post("/trade/action")
async def trade_action(
    action: TradeAction,
    current_user: User = Depends(get_current_user)
):
    """Accept, decline, or modify trade"""
    # TODO: Process trade action
    
    if action.action == "accept":
        # Execute trade - transfer items and currency
        pass
    
    return {"success": True, "action": action.action}


# ============================================================================
# SOCIAL FEATURES
# ============================================================================

@social_router.post("/friend/request")
async def send_friend_request(
    recipient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send friend request"""
    request = FriendRequest(
        requester_id=current_user.id,
        recipient_id=recipient_id,
        created_at=datetime.utcnow()
    )
    
    # TODO: Store and notify recipient
    
    return {"success": True, "request": request}


@social_router.get("/friends")
async def get_friends_list(
    current_user: User = Depends(get_current_user)
):
    """Get user's friends list"""
    # TODO: Fetch from database
    
    return {"friends": [], "blocked": []}


@social_router.post("/message/send")
async def send_player_message(
    recipient_id: int,
    content: str,
    current_user: User = Depends(get_current_user)
):
    """Send private message to player"""
    message = PlayerMessage(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        content=content,
        timestamp=datetime.utcnow()
    )
    
    # TODO: Store and notify recipient via WebSocket
    
    return {"success": True, "message": message}


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@multiplayer_router.post("/session/create", response_model=MultiplayerSession)
async def create_multiplayer_session(
    name: str,
    campaign: str,
    max_players: int = 10,
    is_public: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Create new multiplayer session"""
    session = MultiplayerSession(
        id=f"session-{datetime.utcnow().timestamp()}",
        name=name,
        host_user_id=current_user.id,
        campaign=campaign,
        max_players=max_players,
        current_players=[current_user.id],
        is_public=is_public,
        created_at=datetime.utcnow()
    )
    
    # Create session in data manager
    data_manager.create_session(session.id, campaign)
    
    return session


@multiplayer_router.post("/session/join")
async def join_session(
    request: SessionJoinRequest,
    current_user: User = Depends(get_current_user)
):
    """Join existing session"""
    # TODO: Validate session exists, check capacity, password, etc.
    
    return {
        "success": True,
        "session_id": request.session_id,
        "user_id": current_user.id
    }


@multiplayer_router.get("/session/list")
async def list_public_sessions(
    current_user: User = Depends(get_current_user)
):
    """List public sessions available to join"""
    # TODO: Fetch public sessions from database
    
    return {"sessions": []}

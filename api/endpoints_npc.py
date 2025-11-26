"""API endpoints for NPC management system."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from .auth import verify_api_key
from .models import ActionResponse
from .models_npc import (
    NPC, CreateNPCRequest, UpdateNPCRequest,
    NPCInteractionRequest, NPCDialogueRequest, NPCTradeRequest,
    NPCCombatRequest, NPCRelationshipUpdateRequest, NPCSpawnRequest,
    NPCListFilter, NPCType
)
from .data_manager import data_manager

# Create router for NPC endpoints
router = APIRouter(prefix="/api/v1/npcs", tags=["NPCs"], dependencies=[Depends(verify_api_key)])


@router.get("/", response_model=Dict[str, Any])
async def list_npcs(
    npc_type: Optional[NPCType] = None,
    faction: Optional[str] = None,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
    location: Optional[str] = None,
    tags: Optional[List[str]] = Query(None)
) -> Dict[str, Any]:
    """
    List all NPCs with optional filtering.
    Supports filtering by type, faction, level range, location, and tags.
    """
    # Load all NPCs from data/npcs directory
    import os
    from pathlib import Path
    
    npcs_path = Path(data_manager.data_path) / "npcs"
    npcs_path.mkdir(parents=True, exist_ok=True)
    
    npcs = []
    for npc_file in npcs_path.glob("*.json"):
        npc_data = data_manager.load_npc(npc_file.stem)
        if npc_data:
            # Apply filters
            if npc_type and npc_data.get("npc_type") != npc_type:
                continue
            if faction and npc_data.get("faction") != faction:
                continue
            if min_level and npc_data.get("lvl", 0) < min_level:
                continue
            if max_level and npc_data.get("lvl", 0) > max_level:
                continue
            if location and npc_data.get("location", {}).get("area") != location:
                continue
            if tags:
                npc_tags = set(npc_data.get("tags", []))
                if not any(tag in npc_tags for tag in tags):
                    continue
            
            npcs.append(npc_data)
    
    return {
        "npcs": npcs,
        "count": len(npcs),
        "filters": {
            "npc_type": npc_type,
            "faction": faction,
            "min_level": min_level,
            "max_level": max_level,
            "location": location,
            "tags": tags
        }
    }


@router.get("/{npc_id}", response_model=NPC)
async def get_npc(npc_id: str) -> NPC:
    """Get a specific NPC by ID."""
    npc_data = data_manager.load_npc(npc_id)
    if not npc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC {npc_id} not found"
        )
    return NPC(**npc_data)


@router.post("/", response_model=Dict[str, Any])
async def create_npc(request: CreateNPCRequest) -> Dict[str, Any]:
    """
    Create a new NPC.
    NPCs can be merchants, enemies, allies, quest-givers, etc.
    """
    # Check if NPC already exists
    existing = data_manager.load_npc(request.npc.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"NPC {request.npc.id} already exists"
        )
    
    # Add metadata
    npc_dict = request.npc.model_dump(by_alias=True)
    if not npc_dict.get("metadata"):
        npc_dict["metadata"] = {}
    npc_dict["metadata"]["created_at"] = datetime.now(timezone.utc).isoformat()
    npc_dict["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Save NPC
    data_manager.save_npc(npc_dict)
    
    return {
        "success": True,
        "message": f"NPC {request.npc.id} created successfully",
        "npc": npc_dict
    }


@router.put("/{npc_id}", response_model=Dict[str, Any])
async def update_npc(npc_id: str, request: UpdateNPCRequest) -> Dict[str, Any]:
    """Update an existing NPC."""
    npc_data = data_manager.load_npc(npc_id)
    if not npc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC {npc_id} not found"
        )
    
    # Apply updates
    npc_data.update(request.updates)
    
    # Update metadata
    if "metadata" not in npc_data:
        npc_data["metadata"] = {}
    npc_data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Save NPC
    data_manager.save_npc(npc_data)
    
    return {
        "success": True,
        "message": f"NPC {npc_id} updated successfully",
        "npc": npc_data
    }


@router.delete("/{npc_id}", response_model=Dict[str, Any])
async def delete_npc(npc_id: str) -> Dict[str, Any]:
    """Delete an NPC."""
    npc_data = data_manager.load_npc(npc_id)
    if not npc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC {npc_id} not found"
        )
    
    # Delete NPC file
    data_manager.delete_npc(npc_id)
    
    return {
        "success": True,
        "message": f"NPC {npc_id} deleted successfully"
    }


@router.post("/interact", response_model=ActionResponse)
async def npc_interaction(request: NPCInteractionRequest) -> ActionResponse:
    """
    Handle player-NPC interaction.
    Supports various interaction types: talk, trade, quest, attack, help, etc.
    """
    # Verify session exists
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Verify NPC exists
    npc_data = data_manager.load_npc(request.npc_id)
    if not npc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC {request.npc_id} not found"
        )
    
    # Create interaction event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "npc_interaction",
        "actor": request.player_id,
        "target": request.npc_id,
        "data": {
            "interaction_type": request.interaction_type,
            "npc_name": npc_data.get("name"),
            "npc_type": npc_data.get("npc_type"),
            **request.data
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Interaction with NPC {npc_data.get('name')} recorded",
        result={"interaction_type": request.interaction_type}
    )


@router.post("/dialogue", response_model=ActionResponse)
async def npc_dialogue(request: NPCDialogueRequest) -> ActionResponse:
    """
    Handle NPC dialogue interaction.
    Returns appropriate dialogue based on category and NPC relationship.
    """
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    npc_data = data_manager.load_npc(request.npc_id)
    if not npc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC {request.npc_id} not found"
        )
    
    # Get dialogue from NPC
    dialogue = npc_data.get("dialogue", {})
    dialogue_options = dialogue.get(request.dialogue_category, [])
    
    # Select dialogue based on relationship or random
    import random
    selected_dialogue = random.choice(dialogue_options) if dialogue_options else f"[No {request.dialogue_category} dialogue configured]"
    
    # Create dialogue event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "npc_dialogue",
        "actor": request.npc_id,
        "target": request.player_id,
        "data": {
            "category": request.dialogue_category,
            "dialogue": selected_dialogue,
            "player_input": request.player_input
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message="Dialogue recorded",
        result={
            "npc_name": npc_data.get("name"),
            "dialogue": selected_dialogue
        }
    )


@router.post("/trade", response_model=ActionResponse)
async def npc_trade(request: NPCTradeRequest) -> ActionResponse:
    """
    Handle trading with NPC.
    Supports buying from and selling to NPCs with price modifiers.
    """
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    npc_data = data_manager.load_npc(request.npc_id)
    if not npc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC {request.npc_id} not found"
        )
    
    # Check if NPC can trade
    trade_info = npc_data.get("trade", {})
    if not trade_info.get("can_trade", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"NPC {npc_data.get('name')} cannot trade"
        )
    
    # Create trade event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "npc_trade",
        "actor": request.player_id,
        "target": request.npc_id,
        "data": {
            "trade_type": request.trade_type,
            "item_id": request.item_id,
            "quantity": request.quantity,
            "buy_rate": trade_info.get("buy_rate", 1.0),
            "sell_rate": trade_info.get("sell_rate", 1.0)
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Trade with {npc_data.get('name')} completed",
        result={
            "trade_type": request.trade_type,
            "item_id": request.item_id,
            "quantity": request.quantity
        }
    )


@router.post("/combat", response_model=ActionResponse)
async def npc_combat(request: NPCCombatRequest) -> ActionResponse:
    """
    Handle NPC combat action.
    NPCs can attack, use abilities, use items, etc.
    """
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    npc_data = data_manager.load_npc(request.npc_id)
    if not npc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC {request.npc_id} not found"
        )
    
    # Create combat event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "npc_combat",
        "actor": request.npc_id,
        "target": request.target_id,
        "data": {
            "action_type": request.action_type,
            "npc_name": npc_data.get("name"),
            "npc_level": npc_data.get("lvl"),
            **request.data
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"NPC {npc_data.get('name')} performed {request.action_type}",
        result={"action_type": request.action_type}
    )


@router.post("/relationship", response_model=ActionResponse)
async def update_npc_relationship(request: NPCRelationshipUpdateRequest) -> ActionResponse:
    """
    Update relationship between NPC and character.
    Tracks reputation, trust, and relationship type.
    """
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    npc_data = data_manager.load_npc(request.npc_id)
    if not npc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC {request.npc_id} not found"
        )
    
    # Create relationship update event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "npc_relationship_update",
        "actor": request.character_id,
        "target": request.npc_id,
        "data": {
            "reputation_change": request.reputation_change,
            "trust_change": request.trust_change,
            "new_relationship_type": request.new_relationship_type.value if request.new_relationship_type else None
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Relationship with {npc_data.get('name')} updated",
        result={
            "reputation_change": request.reputation_change,
            "trust_change": request.trust_change
        }
    )


@router.post("/spawn", response_model=ActionResponse)
async def spawn_npc(request: NPCSpawnRequest) -> ActionResponse:
    """
    Spawn an NPC instance in a session.
    Creates an instance from an NPC template.
    """
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    npc_data = data_manager.load_npc(request.npc_id)
    if not npc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC {request.npc_id} not found"
        )
    
    # Generate instance ID if not provided
    instance_id = request.instance_id or f"{request.npc_id}-{datetime.now(timezone.utc).timestamp()}"
    
    # Create spawn event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "npc_spawn",
        "actor": "system",
        "data": {
            "npc_template_id": request.npc_id,
            "instance_id": instance_id,
            "location": request.location,
            "npc_data": npc_data
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"NPC {npc_data.get('name')} spawned at {request.location}",
        result={
            "instance_id": instance_id,
            "location": request.location
        }
    )


@router.get("/types", response_model=Dict[str, Any])
async def get_npc_types() -> Dict[str, Any]:
    """
    Get all available NPC types with descriptions.
    Useful for understanding NPC categories.
    """
    return {
        "types": {
            "merchant": "Sells and buys items, focused on trading",
            "enemy": "Hostile NPC, will attack on sight",
            "ally": "Friendly NPC, may help in combat",
            "neutral": "Neither hostile nor friendly",
            "quest_giver": "Provides quests to players",
            "guard": "Protects areas, enforces rules",
            "companion": "Can join player party",
            "boss": "Powerful enemy, usually unique",
            "vendor": "Specialized merchant",
            "trainer": "Teaches skills or abilities",
            "innkeeper": "Manages inn/tavern services",
            "blacksmith": "Repairs and crafts items",
            "custom": "Custom NPC type"
        }
    }

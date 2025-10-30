"""Extended API endpoints for enhanced RPG features."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime, timezone

from .auth import verify_api_key
from .models import ActionResponse
from .models_extended import (
    CharacterExtended,
    EquipItemRequest,
    UnequipItemRequest,
    CraftItemRequest,
    UseItemRequest,
    TradeItemRequest,
    ApplyStatusEffectRequest,
    LearnAbilityRequest,
    LearnRecipeRequest,
    ModifyAttributeRequest
)
from .data_manager import data_manager

# Create router for extended endpoints
router = APIRouter(prefix="/api/v1/extended", tags=["Extended Features"], dependencies=[Depends(verify_api_key)])


@router.get("/characters/{character_id}", response_model=CharacterExtended)
async def get_extended_character(character_id: str) -> CharacterExtended:
    """
    Get a character with full extended properties.
    Supports inventory, equipment, skills, abilities, crafting, etc.
    """
    char_data = data_manager.load_character(character_id)
    if not char_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found"
        )
    return CharacterExtended(**char_data)


@router.post("/equip-item", response_model=ActionResponse)
async def equip_item(request: EquipItemRequest, session_id: str) -> ActionResponse:
    """
    Equip an item from inventory to an equipment slot.
    """
    # Verify session exists
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Create event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "equip_item",
        "actor": request.character_id,
        "data": {
            "character_id": request.character_id,
            "item_id": request.item_id,
            "slot": request.slot
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Item {request.item_id} equipped to {request.slot}",
        result={"slot": request.slot, "item_id": request.item_id}
    )


@router.post("/unequip-item", response_model=ActionResponse)
async def unequip_item(request: UnequipItemRequest, session_id: str) -> ActionResponse:
    """
    Unequip an item from an equipment slot back to inventory.
    """
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "unequip_item",
        "actor": request.character_id,
        "data": {
            "character_id": request.character_id,
            "slot": request.slot
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Item unequipped from {request.slot}",
        result={"slot": request.slot}
    )


@router.post("/craft-item", response_model=ActionResponse)
async def craft_item(request: CraftItemRequest, session_id: str) -> ActionResponse:
    """
    Craft an item using a known recipe.
    """
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "craft_item",
        "actor": request.character_id,
        "data": {
            "character_id": request.character_id,
            "recipe_id": request.recipe_id,
            "quantity": request.quantity
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Crafted {request.quantity}x {request.recipe_id}",
        result={"recipe_id": request.recipe_id, "quantity": request.quantity}
    )


@router.post("/use-item", response_model=ActionResponse)
async def use_item(request: UseItemRequest, session_id: str) -> ActionResponse:
    """
    Use a consumable item.
    """
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "use_item",
        "actor": request.character_id,
        "target": request.target_id,
        "data": {
            "character_id": request.character_id,
            "item_id": request.item_id,
            "target_id": request.target_id
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Used item {request.item_id}",
        result={"item_id": request.item_id}
    )


@router.post("/trade-item", response_model=ActionResponse)
async def trade_item(request: TradeItemRequest, session_id: str) -> ActionResponse:
    """
    Trade items between characters.
    """
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "trade_item",
        "actor": request.from_character_id,
        "target": request.to_character_id,
        "data": {
            "from_character_id": request.from_character_id,
            "to_character_id": request.to_character_id,
            "item_id": request.item_id,
            "quantity": request.quantity
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Traded {request.quantity}x {request.item_id}",
        result={"from": request.from_character_id, "to": request.to_character_id, "quantity": request.quantity}
    )


@router.post("/apply-status-effect", response_model=ActionResponse)
async def apply_status_effect(request: ApplyStatusEffectRequest, session_id: str) -> ActionResponse:
    """
    Apply a status effect (buff/debuff) to a character.
    """
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "apply_status_effect",
        "actor": request.character_id,
        "data": {
            "character_id": request.character_id,
            "effect": request.effect.model_dump()
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Applied status effect {request.effect.name}",
        result={"effect": request.effect.name, "type": request.effect.type}
    )


@router.post("/learn-ability", response_model=ActionResponse)
async def learn_ability(request: LearnAbilityRequest, session_id: str) -> ActionResponse:
    """
    Learn a new ability or spell.
    """
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "learn_ability",
        "actor": request.character_id,
        "data": {
            "character_id": request.character_id,
            "ability": request.ability.model_dump()
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Learned ability {request.ability.name}",
        result={"ability": request.ability.name, "type": request.ability.type}
    )


@router.post("/learn-recipe", response_model=ActionResponse)
async def learn_recipe(request: LearnRecipeRequest, session_id: str) -> ActionResponse:
    """
    Learn a new crafting recipe.
    """
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "learn_recipe",
        "actor": request.character_id,
        "data": {
            "character_id": request.character_id,
            "recipe_id": request.recipe_id
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Learned recipe {request.recipe_id}",
        result={"recipe_id": request.recipe_id}
    )


@router.post("/modify-attribute", response_model=ActionResponse)
async def modify_attribute(request: ModifyAttributeRequest, session_id: str) -> ActionResponse:
    """
    Modify a character attribute (speed, armor_class, etc.).
    """
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "modify_attribute",
        "actor": request.character_id,
        "data": {
            "character_id": request.character_id,
            "attribute": request.attribute,
            "value": request.value,
            "operation": request.operation
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Modified attribute {request.attribute}",
        result={"attribute": request.attribute, "value": request.value, "operation": request.operation}
    )

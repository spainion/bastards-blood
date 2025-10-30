"""Pydantic models for the RPG API."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Event types for game actions."""
    NOTE = "note"
    CHECK = "check"
    ATTACK = "attack"
    DAMAGE = "damage"
    HEAL = "heal"
    GAIN_ITEM = "gain_item"
    LOSE_ITEM = "lose_item"
    STATUS = "status"
    CREATE_CHAR = "create_char"
    UPDATE_CHAR = "update_char"
    CUSTOM = "custom"
    # Extended event types for enhanced features
    EQUIP_ITEM = "equip_item"
    UNEQUIP_ITEM = "unequip_item"
    CRAFT_ITEM = "craft_item"
    USE_ITEM = "use_item"
    TRADE_ITEM = "trade_item"
    APPLY_STATUS_EFFECT = "apply_status_effect"
    REMOVE_STATUS_EFFECT = "remove_status_effect"
    LEARN_ABILITY = "learn_ability"
    USE_ABILITY = "use_ability"
    LEARN_RECIPE = "learn_recipe"
    GAIN_XP = "gain_xp"
    LEVEL_UP = "level_up"
    MODIFY_STAT = "modify_stat"
    MODIFY_ATTRIBUTE = "modify_attribute"
    MODIFY_RESOURCE = "modify_resource"


class HPStats(BaseModel):
    """Health points statistics."""
    max: int = Field(..., ge=0, description="Maximum HP")
    current: int = Field(..., ge=0, description="Current HP")


class CharacterStats(BaseModel):
    """Character statistics."""
    STR: Optional[int] = Field(None, description="Strength")
    DEX: Optional[int] = Field(None, description="Dexterity")
    CON: Optional[int] = Field(None, description="Constitution")
    INT: Optional[int] = Field(None, description="Intelligence")
    WIS: Optional[int] = Field(None, description="Wisdom")
    CHA: Optional[int] = Field(None, description="Charisma")


class Character(BaseModel):
    """Character model."""
    id: str = Field(..., pattern="^[a-z0-9-]+$", description="Character ID")
    name: str = Field(..., description="Character name")
    class_name: Optional[str] = Field(None, alias="class", description="Character class")
    lvl: Optional[int] = Field(None, ge=0, description="Character level")
    stats: CharacterStats = Field(..., description="Character statistics")
    hp: HPStats = Field(..., description="Health points")
    inventory: Optional[List[str]] = Field(default_factory=list, description="Character inventory")
    tags: Optional[List[str]] = Field(default_factory=list, description="Character tags")
    notes: Optional[str] = Field(None, description="Character notes")
    
    class Config:
        populate_by_name = True


class Event(BaseModel):
    """Game event model."""
    id: str = Field(..., pattern="^e_[a-z0-9]{8}$", description="Event ID")
    ts: datetime = Field(..., description="Event timestamp")
    t: EventType = Field(..., description="Event type")
    actor: Optional[str] = Field(None, description="Actor character ID")
    target: Optional[str] = Field(None, description="Target character ID")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Event data")
    result: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Event result")


class Session(BaseModel):
    """Game session model."""
    id: str = Field(..., description="Session ID")
    campaign: str = Field(..., description="Campaign name")
    events: List[Event] = Field(default_factory=list, description="Session events")


class ActionRequest(BaseModel):
    """Request for a player action."""
    session_id: str = Field(..., description="Session ID")
    actor_id: str = Field(..., description="Acting character ID")
    action_type: EventType = Field(..., description="Type of action")
    target_id: Optional[str] = Field(None, description="Target character ID")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional action data")


class SpeechRequest(BaseModel):
    """Request for player speech/dialogue."""
    session_id: str = Field(..., description="Session ID")
    character_id: str = Field(..., description="Speaking character ID")
    text: str = Field(..., description="Speech text")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Speech context")


class GameStateResponse(BaseModel):
    """Response with current game state."""
    characters: Dict[str, Character] = Field(default_factory=dict, description="All characters")
    session_id: str = Field(..., description="Current session ID")
    campaign: str = Field(..., description="Campaign name")
    event_count: int = Field(..., description="Total events in session")


class ActionResponse(BaseModel):
    """Response after an action."""
    success: bool = Field(..., description="Whether action succeeded")
    event_id: str = Field(..., description="Generated event ID")
    message: str = Field(..., description="Response message")
    result: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action result")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current timestamp")

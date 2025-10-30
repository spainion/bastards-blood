"""Pydantic models for NPC management system."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class NPCType(str, Enum):
    """NPC types defining role and behavior."""
    MERCHANT = "merchant"
    ENEMY = "enemy"
    ALLY = "ally"
    NEUTRAL = "neutral"
    QUEST_GIVER = "quest_giver"
    GUARD = "guard"
    COMPANION = "companion"
    BOSS = "boss"
    VENDOR = "vendor"
    TRAINER = "trainer"
    INNKEEPER = "innkeeper"
    BLACKSMITH = "blacksmith"
    CUSTOM = "custom"


class AggressionLevel(str, Enum):
    """NPC combat behavior."""
    PASSIVE = "passive"
    DEFENSIVE = "defensive"
    NEUTRAL = "neutral"
    AGGRESSIVE = "aggressive"
    HOSTILE = "hostile"


class DispositionLevel(str, Enum):
    """NPC general attitude."""
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    UNFRIENDLY = "unfriendly"
    HOSTILE = "hostile"


class RelationshipType(str, Enum):
    """Type of relationship."""
    ENEMY = "enemy"
    RIVAL = "rival"
    NEUTRAL = "neutral"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    ALLY = "ally"
    FAMILY = "family"
    LOVER = "lover"


class AIType(str, Enum):
    """AI behavior type."""
    SIMPLE = "simple"
    TACTICAL = "tactical"
    SUPPORT = "support"
    RANGED = "ranged"
    MELEE = "melee"
    CASTER = "caster"
    CUSTOM = "custom"


class NPCBehavior(BaseModel):
    """NPC behavior patterns."""
    aggression: Optional[AggressionLevel] = Field(None, description="Combat behavior")
    disposition: Optional[DispositionLevel] = Field(None, description="General attitude")
    wander: Optional[bool] = Field(None, description="Whether NPC wanders")
    patrol_route: Optional[List[str]] = Field(default_factory=list, description="Patrol locations")
    flee_threshold: Optional[int] = Field(None, description="HP % at which NPC flees")
    call_for_help: Optional[bool] = Field(None, description="Whether NPC calls for help")


class NPCDialogue(BaseModel):
    """NPC dialogue options."""
    greeting: Optional[List[str]] = Field(default_factory=list, description="Greeting dialogues")
    farewell: Optional[List[str]] = Field(default_factory=list, description="Farewell dialogues")
    trade: Optional[List[str]] = Field(default_factory=list, description="Trade dialogues")
    combat: Optional[List[str]] = Field(default_factory=list, description="Combat taunts")
    custom: Optional[Dict[str, List[str]]] = Field(default_factory=dict, description="Custom categories")


class NPCTrade(BaseModel):
    """NPC trading information."""
    can_trade: bool = Field(False, description="Whether NPC can trade")
    buy_rate: Optional[float] = Field(1.0, description="Price multiplier for buying from NPC")
    sell_rate: Optional[float] = Field(1.0, description="Price multiplier for selling to NPC")
    currency: Optional[Dict[str, int]] = Field(default_factory=dict, description="NPC currency")
    trade_inventory: Optional[List[str]] = Field(default_factory=list, description="Items for trade")
    preferred_items: Optional[List[str]] = Field(default_factory=list, description="Preferred items")


class NPCQuest(BaseModel):
    """NPC quest-giving information."""
    can_give_quests: bool = Field(False, description="Whether NPC gives quests")
    active_quests: Optional[List[str]] = Field(default_factory=list, description="Quest IDs offered")
    completed_quests: Optional[List[str]] = Field(default_factory=list, description="Completed quests")


class NPCRelationship(BaseModel):
    """Relationship with player or other NPC."""
    reputation: int = Field(0, description="Reputation value (-100 to 100)")
    relationship_type: RelationshipType = Field(RelationshipType.NEUTRAL, description="Relationship type")
    trust_level: int = Field(50, ge=0, le=100, description="Trust level (0-100)")


class ScheduleActivity(BaseModel):
    """Scheduled activity."""
    time: str = Field(..., description="Time of day")
    location: str = Field(..., description="Location")
    activity: str = Field(..., description="Activity description")
    duration: Optional[int] = Field(None, description="Duration in minutes")


class NPCSchedule(BaseModel):
    """NPC daily schedule."""
    enabled: bool = Field(False, description="Whether schedule is active")
    activities: Optional[List[ScheduleActivity]] = Field(default_factory=list, description="Scheduled activities")


class NPCAI(BaseModel):
    """AI behavior settings."""
    ai_type: Optional[AIType] = Field(AIType.SIMPLE, description="AI behavior type")
    combat_style: Optional[str] = Field(None, description="Preferred combat style")
    target_priority: Optional[List[str]] = Field(default_factory=list, description="Target priority")
    use_abilities: bool = Field(True, description="Whether AI uses abilities")
    use_items: bool = Field(True, description="Whether AI uses items")


class NPCLocation(BaseModel):
    """NPC location information."""
    area: Optional[str] = Field(None, description="Current area")
    position: Optional[Dict[str, float]] = Field(default_factory=dict, description="Position coordinates")
    home_location: Optional[str] = Field(None, description="Home location")


class NPCSpawning(BaseModel):
    """NPC spawning information."""
    can_respawn: bool = Field(False, description="Whether NPC can respawn")
    respawn_time: Optional[int] = Field(None, description="Respawn time in seconds")
    spawn_location: Optional[str] = Field(None, description="Spawn location")
    spawn_condition: Optional[str] = Field(None, description="Spawn condition")


class LootDrop(BaseModel):
    """Loot drop information."""
    item_id: str = Field(..., description="Item ID")
    chance: float = Field(..., ge=0, le=1, description="Drop chance (0-1)")
    quantity_min: int = Field(1, ge=1, description="Minimum quantity")
    quantity_max: int = Field(1, ge=1, description="Maximum quantity")


class CurrencyDrop(BaseModel):
    """Currency drop information."""
    min: int = Field(0, ge=0, description="Minimum amount")
    max: int = Field(0, ge=0, description="Maximum amount")


class NPCLoot(BaseModel):
    """NPC loot table."""
    drop_chance: float = Field(1.0, ge=0, le=1, description="Base drop chance")
    guaranteed_drops: Optional[List[str]] = Field(default_factory=list, description="Guaranteed drops")
    possible_drops: Optional[List[LootDrop]] = Field(default_factory=list, description="Possible drops")
    currency_drops: Optional[Dict[str, CurrencyDrop]] = Field(default_factory=dict, description="Currency drops")


class NPCAppearance(BaseModel):
    """NPC physical appearance."""
    height: Optional[str] = Field(None, description="Height")
    build: Optional[str] = Field(None, description="Body build")
    hair_color: Optional[str] = Field(None, description="Hair color")
    eye_color: Optional[str] = Field(None, description="Eye color")
    skin_tone: Optional[str] = Field(None, description="Skin tone")
    age: Optional[int] = Field(None, description="Age")
    distinctive_features: Optional[List[str]] = Field(default_factory=list, description="Distinctive features")


class NPCVoice(BaseModel):
    """NPC voice characteristics."""
    pitch: Optional[str] = Field(None, description="Voice pitch")
    accent: Optional[str] = Field(None, description="Accent")
    speech_pattern: Optional[str] = Field(None, description="Speech pattern")


class NPCCustomization(BaseModel):
    """NPC appearance and customization."""
    appearance: Optional[NPCAppearance] = Field(None, description="Physical appearance")
    voice: Optional[NPCVoice] = Field(None, description="Voice characteristics")


class NPCMetadata(BaseModel):
    """NPC metadata."""
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="Creator")
    version: Optional[str] = Field(None, description="Version")


class NPC(BaseModel):
    """Complete NPC model."""
    # Core properties
    id: str = Field(..., pattern="^npc-[a-z0-9-]+$", description="NPC ID with 'npc-' prefix")
    name: str = Field(..., description="NPC name")
    npc_type: NPCType = Field(..., description="NPC type")
    class_name: Optional[str] = Field(None, alias="class", description="NPC class")
    race: Optional[str] = Field(None, description="NPC race")
    lvl: Optional[int] = Field(None, ge=0, description="NPC level")
    faction: Optional[str] = Field(None, description="Faction affiliation")
    
    # Stats and attributes
    stats: Dict[str, int] = Field(..., description="Core statistics")
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Derived attributes")
    
    # Hit points and resources
    hp: Dict[str, int] = Field(..., description="Hit points")
    resources: Optional[Dict[str, Dict[str, int]]] = Field(default_factory=dict, description="Resources")
    
    # Inventory and equipment (reuse from extended character models)
    inventory: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Inventory")
    equipment: Optional[Dict[str, Dict[str, Any]]] = Field(default_factory=dict, description="Equipment")
    
    # Abilities
    abilities: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Abilities")
    
    # NPC-specific properties
    behavior: Optional[NPCBehavior] = Field(None, description="Behavior patterns")
    dialogue: Optional[NPCDialogue] = Field(None, description="Dialogue options")
    trade: Optional[NPCTrade] = Field(None, description="Trading information")
    quest: Optional[NPCQuest] = Field(None, description="Quest information")
    relationships: Optional[Dict[str, NPCRelationship]] = Field(default_factory=dict, description="Relationships")
    schedule: Optional[NPCSchedule] = Field(None, description="Daily schedule")
    ai: Optional[NPCAI] = Field(None, description="AI settings")
    location: Optional[NPCLocation] = Field(None, description="Location")
    spawning: Optional[NPCSpawning] = Field(None, description="Spawning info")
    loot: Optional[NPCLoot] = Field(None, description="Loot table")
    status_effects: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Status effects")
    customization: Optional[NPCCustomization] = Field(None, description="Customization")
    
    # Metadata
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags")
    notes: Optional[str] = Field(None, description="Notes")
    metadata: Optional[NPCMetadata] = Field(None, description="Metadata")
    
    class Config:
        populate_by_name = True


# Request models for NPC operations

class CreateNPCRequest(BaseModel):
    """Request to create an NPC."""
    npc: NPC = Field(..., description="NPC data")


class UpdateNPCRequest(BaseModel):
    """Request to update an NPC."""
    npc_id: str = Field(..., description="NPC ID")
    updates: Dict[str, Any] = Field(..., description="Fields to update")


class NPCInteractionRequest(BaseModel):
    """Request for player-NPC interaction."""
    session_id: str = Field(..., description="Session ID")
    player_id: str = Field(..., description="Player character ID")
    npc_id: str = Field(..., description="NPC ID")
    interaction_type: str = Field(..., description="Type of interaction")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Interaction data")


class NPCDialogueRequest(BaseModel):
    """Request for NPC dialogue."""
    session_id: str = Field(..., description="Session ID")
    player_id: str = Field(..., description="Player character ID")
    npc_id: str = Field(..., description="NPC ID")
    dialogue_category: str = Field(..., description="Dialogue category")
    player_input: Optional[str] = Field(None, description="Player dialogue input")


class NPCTradeRequest(BaseModel):
    """Request to trade with NPC."""
    session_id: str = Field(..., description="Session ID")
    player_id: str = Field(..., description="Player character ID")
    npc_id: str = Field(..., description="NPC ID")
    trade_type: str = Field(..., description="'buy' or 'sell'")
    item_id: str = Field(..., description="Item ID")
    quantity: int = Field(1, ge=1, description="Quantity")


class NPCCombatRequest(BaseModel):
    """Request for NPC combat action."""
    session_id: str = Field(..., description="Session ID")
    npc_id: str = Field(..., description="NPC ID")
    target_id: str = Field(..., description="Target ID")
    action_type: str = Field(..., description="Combat action type")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action data")


class NPCRelationshipUpdateRequest(BaseModel):
    """Request to update NPC relationship."""
    session_id: str = Field(..., description="Session ID")
    npc_id: str = Field(..., description="NPC ID")
    character_id: str = Field(..., description="Character ID")
    reputation_change: Optional[int] = Field(None, description="Reputation change")
    trust_change: Optional[int] = Field(None, description="Trust level change")
    new_relationship_type: Optional[RelationshipType] = Field(None, description="New relationship type")


class NPCSpawnRequest(BaseModel):
    """Request to spawn an NPC."""
    session_id: str = Field(..., description="Session ID")
    npc_id: str = Field(..., description="NPC template ID")
    location: str = Field(..., description="Spawn location")
    instance_id: Optional[str] = Field(None, description="Optional instance ID for unique spawn")


class NPCListFilter(BaseModel):
    """Filter for listing NPCs."""
    npc_type: Optional[NPCType] = Field(None, description="Filter by NPC type")
    faction: Optional[str] = Field(None, description="Filter by faction")
    min_level: Optional[int] = Field(None, description="Minimum level")
    max_level: Optional[int] = Field(None, description="Maximum level")
    location: Optional[str] = Field(None, description="Filter by location")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")

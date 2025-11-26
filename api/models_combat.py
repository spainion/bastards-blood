"""Pydantic models for combat system, enemies, and mobs."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class EnemyType(str, Enum):
    """Enemy/mob types."""
    BEAST = "beast"
    UNDEAD = "undead"
    DEMON = "demon"
    HUMANOID = "humanoid"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    CONSTRUCT = "construct"
    ABERRATION = "aberration"
    GOBLIN = "goblin"
    ORC = "orc"
    TROLL = "troll"
    BOSS = "boss"
    CUSTOM = "custom"


class DamageType(str, Enum):
    """Damage types."""
    PHYSICAL = "physical"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    DARK = "dark"
    ARCANE = "arcane"


class AIBehavior(str, Enum):
    """AI behavior patterns."""
    PASSIVE = "passive"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    PATROL = "patrol"
    AMBUSH = "ambush"
    FLEE_LOW_HP = "flee_low_hp"
    CALL_FOR_HELP = "call_for_help"


class Enemy(BaseModel):
    """Enemy/mob model."""
    id: str = Field(..., description="Enemy ID")
    name: str = Field(..., description="Enemy name")
    enemy_type: EnemyType = Field(..., description="Enemy type")
    level: int = Field(default=1, ge=1, le=120, description="Enemy level")
    
    # Stats
    stats: Dict[str, int] = Field(..., description="Base stats (STR, DEX, CON, etc.)")
    hp: Dict[str, int] = Field(..., description="HP with max and current")
    
    # Combat stats
    damage_min: int = Field(default=1, ge=1, description="Minimum damage")
    damage_max: int = Field(default=10, ge=1, description="Maximum damage")
    armor: int = Field(default=0, ge=0, description="Armor/defense rating")
    attack_speed: float = Field(default=1.0, ge=0.1, le=5.0, description="Attacks per second")
    aggro_range: float = Field(default=10.0, ge=0.0, description="Aggro detection range")
    
    # Rewards
    xp_reward: int = Field(default=10, ge=0, description="XP given on defeat")
    loot_table: Dict[str, Any] = Field(default_factory=dict, description="Loot drops")
    
    # Location
    location: Optional[Dict[str, float]] = Field(None, description="Current location (x, y, z)")
    spawn_location: Optional[Dict[str, float]] = Field(None, description="Spawn point")
    region: Optional[str] = Field(None, description="Region/zone")
    
    # AI and behavior
    ai_type: AIBehavior = Field(default=AIBehavior.AGGRESSIVE, description="AI behavior")
    abilities: List[str] = Field(default_factory=list, description="Special abilities")
    
    # State
    is_alive: bool = Field(default=True, description="Is enemy alive")
    respawn_time: int = Field(default=300, ge=0, description="Respawn time in seconds")


class CombatAction(BaseModel):
    """Combat action request."""
    session_id: str = Field(..., description="Session ID")
    attacker_id: str = Field(..., description="Attacker character/enemy ID")
    defender_id: str = Field(..., description="Defender character/enemy ID")
    action_type: str = Field(..., description="Action type (attack, cast_spell, use_ability)")
    ability_id: Optional[str] = Field(None, description="Ability/spell ID if applicable")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional action data")


class CombatResult(BaseModel):
    """Combat action result."""
    success: bool = Field(..., description="Was action successful")
    damage_dealt: int = Field(default=0, description="Damage dealt")
    damage_type: DamageType = Field(default=DamageType.PHYSICAL, description="Damage type")
    was_critical: bool = Field(default=False, description="Was it a critical hit")
    was_miss: bool = Field(default=False, description="Did the attack miss")
    
    # State changes
    attacker_hp: Dict[str, int] = Field(..., description="Attacker HP (max, current)")
    defender_hp: Dict[str, int] = Field(..., description="Defender HP (max, current)")
    defender_defeated: bool = Field(default=False, description="Was defender defeated")
    
    # Rewards (if defender defeated)
    xp_gained: int = Field(default=0, description="XP gained")
    loot_dropped: List[Dict[str, Any]] = Field(default_factory=list, description="Loot items")
    
    # Messages
    message: str = Field(..., description="Combat log message")
    details: List[str] = Field(default_factory=list, description="Detailed combat log")


class SpawnEnemyRequest(BaseModel):
    """Request to spawn an enemy."""
    session_id: str = Field(..., description="Session ID")
    enemy_template: str = Field(..., description="Enemy template name (goblin, orc, dragon, etc.)")
    location: Dict[str, float] = Field(..., description="Spawn location (x, y, z)")
    region: Optional[str] = Field(None, description="Region/zone")
    level_override: Optional[int] = Field(None, ge=1, le=120, description="Override enemy level")
    quantity: int = Field(default=1, ge=1, le=100, description="Number to spawn")


class EnemyListQuery(BaseModel):
    """Query parameters for listing enemies."""
    session_id: str = Field(..., description="Session ID")
    region: Optional[str] = Field(None, description="Filter by region")
    enemy_type: Optional[EnemyType] = Field(None, description="Filter by type")
    alive_only: bool = Field(default=True, description="Only show alive enemies")
    within_range: Optional[float] = Field(None, description="Within range of player")


class CombatStats(BaseModel):
    """Combat statistics for a character or enemy."""
    total_damage_dealt: int = Field(default=0, description="Total damage dealt")
    total_damage_taken: int = Field(default=0, description="Total damage taken")
    kills: int = Field(default=0, description="Total kills")
    deaths: int = Field(default=0, description="Total deaths")
    critical_hits: int = Field(default=0, description="Critical hits landed")
    attacks_made: int = Field(default=0, description="Total attacks made")
    attacks_hit: int = Field(default=0, description="Attacks that hit")
    hit_rate: float = Field(default=0.0, description="Hit rate percentage")

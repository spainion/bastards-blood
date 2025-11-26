"""Pydantic models for world coordinates, movement, and spatial systems."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class MovementType(str, Enum):
    """Types of movement."""
    WALK = "walk"
    RUN = "run"
    SPRINT = "sprint"
    SNEAK = "sneak"
    CRAWL = "crawl"
    SWIM = "swim"
    FLY = "fly"
    TELEPORT = "teleport"
    CLIMB = "climb"
    JUMP = "jump"


class TerrainType(str, Enum):
    """Types of terrain."""
    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    WATER = "water"
    SWAMP = "swamp"
    URBAN = "urban"
    DUNGEON = "dungeon"
    CAVE = "cave"
    ROAD = "road"
    CUSTOM = "custom"


class WorldCoordinates(BaseModel):
    """3D world coordinates with optional region/zone."""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(0.0, description="Z coordinate (elevation)")
    region: Optional[str] = Field(None, description="Region or zone name")
    area: Optional[str] = Field(None, description="Specific area within region")
    
    def distance_to(self, other: 'WorldCoordinates') -> float:
        """Calculate Euclidean distance to another coordinate."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5
    
    def distance_2d(self, other: 'WorldCoordinates') -> float:
        """Calculate 2D distance (ignoring elevation)."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class MovementSpeed(BaseModel):
    """Movement speed configuration."""
    base_speed: float = Field(30.0, description="Base movement speed")
    walk_speed: float = Field(30.0, description="Walking speed")
    run_speed: float = Field(60.0, description="Running speed")
    sprint_speed: float = Field(90.0, description="Sprint speed")
    sneak_speed: float = Field(15.0, description="Sneaking speed")
    swim_speed: float = Field(20.0, description="Swimming speed")
    fly_speed: Optional[float] = Field(None, description="Flying speed (if capable)")
    climb_speed: float = Field(15.0, description="Climbing speed")


class Location(BaseModel):
    """Complete location information."""
    coordinates: WorldCoordinates = Field(..., description="World coordinates")
    facing: Optional[float] = Field(None, ge=0, lt=360, description="Facing direction in degrees (0-359)")
    terrain: Optional[TerrainType] = Field(None, description="Current terrain type")
    elevation_name: Optional[str] = Field(None, description="Elevation name (ground, first floor, etc.)")
    landmarks: Optional[List[str]] = Field(default_factory=list, description="Nearby landmarks")
    description: Optional[str] = Field(None, description="Location description")


class MovementAction(BaseModel):
    """Movement action details."""
    character_id: str = Field(..., description="Character or NPC ID")
    movement_type: MovementType = Field(..., description="Type of movement")
    from_location: Location = Field(..., description="Starting location")
    to_location: Location = Field(..., description="Destination location")
    distance: Optional[float] = Field(None, description="Distance traveled")
    duration: Optional[float] = Field(None, description="Movement duration in seconds")
    path: Optional[List[WorldCoordinates]] = Field(None, description="Path taken")
    stamina_cost: Optional[float] = Field(None, description="Stamina/energy cost")


class SkillCheck(BaseModel):
    """Skill check configuration."""
    skill_name: str = Field(..., description="Name of the skill")
    difficulty: int = Field(..., ge=1, le=30, description="Difficulty class (DC)")
    modifier: Optional[int] = Field(0, description="Total modifier")
    roll: Optional[int] = Field(None, ge=1, le=20, description="D20 roll result")
    success: Optional[bool] = Field(None, description="Whether check succeeded")
    critical: Optional[bool] = Field(None, description="Critical success/failure")


class Skill(BaseModel):
    """Character or NPC skill."""
    name: str = Field(..., description="Skill name")
    level: int = Field(0, ge=0, description="Skill level")
    xp: int = Field(0, ge=0, description="Current XP in skill")
    xp_to_next: Optional[int] = Field(None, description="XP needed for next level")
    base_attribute: Optional[str] = Field(None, description="Base attribute (e.g., DEX, INT)")
    bonus: int = Field(0, description="Additional bonus")
    description: Optional[str] = Field(None, description="Skill description")


class ActionType(str, Enum):
    """Types of in-game actions."""
    # Movement
    MOVE = "move"
    TELEPORT = "teleport"
    # Interaction
    INTERACT = "interact"
    USE = "use"
    EXAMINE = "examine"
    SEARCH = "search"
    OPEN = "open"
    CLOSE = "close"
    LOCK = "lock"
    UNLOCK = "unlock"
    # Combat
    ATTACK = "attack"
    DEFEND = "defend"
    DODGE = "dodge"
    PARRY = "parry"
    # Skills
    SKILL_CHECK = "skill_check"
    CAST_SPELL = "cast_spell"
    USE_ABILITY = "use_ability"
    # Social
    TALK = "talk"
    PERSUADE = "persuade"
    INTIMIDATE = "intimidate"
    DECEIVE = "deceive"
    # Other
    REST = "rest"
    CRAFT = "craft"
    GATHER = "gather"
    CUSTOM = "custom"


class GameAction(BaseModel):
    """Generic game action."""
    session_id: str = Field(..., description="Session ID")
    actor_id: str = Field(..., description="Character performing action")
    action_type: ActionType = Field(..., description="Type of action")
    target_id: Optional[str] = Field(None, description="Target of action")
    target_location: Optional[WorldCoordinates] = Field(None, description="Target location")
    skill_check: Optional[SkillCheck] = Field(None, description="Associated skill check")
    duration: Optional[float] = Field(None, description="Action duration in seconds")
    cost: Optional[Dict[str, float]] = Field(None, description="Resource costs")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional action data")


class Zone(BaseModel):
    """Game zone or area definition."""
    id: str = Field(..., description="Zone ID")
    name: str = Field(..., description="Zone name")
    description: Optional[str] = Field(None, description="Zone description")
    bounds: Optional[Dict[str, float]] = Field(None, description="Bounding box (min_x, max_x, min_y, max_y, min_z, max_z)")
    terrain: Optional[TerrainType] = Field(None, description="Primary terrain type")
    level_range: Optional[Dict[str, int]] = Field(None, description="Recommended level range")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Zone properties")
    poi: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Points of interest")


class PathfindingRequest(BaseModel):
    """Request to find path between two points."""
    session_id: str = Field(..., description="Session ID")
    character_id: str = Field(..., description="Character ID")
    start: WorldCoordinates = Field(..., description="Start position")
    end: WorldCoordinates = Field(..., description="End position")
    movement_type: MovementType = Field(MovementType.WALK, description="Movement type")
    avoid_terrain: Optional[List[TerrainType]] = Field(None, description="Terrain types to avoid")
    max_distance: Optional[float] = Field(None, description="Maximum path distance")


class MoveCharacterRequest(BaseModel):
    """Request to move a character."""
    session_id: str = Field(..., description="Session ID")
    character_id: str = Field(..., description="Character or NPC ID")
    destination: WorldCoordinates = Field(..., description="Destination coordinates")
    movement_type: MovementType = Field(MovementType.WALK, description="Movement type")
    auto_path: bool = Field(True, description="Automatically calculate path")


class TeleportRequest(BaseModel):
    """Request to teleport a character."""
    session_id: str = Field(..., description="Session ID")
    character_id: str = Field(..., description="Character or NPC ID")
    destination: WorldCoordinates = Field(..., description="Destination coordinates")
    reason: Optional[str] = Field(None, description="Reason for teleport")


class SkillCheckRequest(BaseModel):
    """Request to perform a skill check."""
    session_id: str = Field(..., description="Session ID")
    character_id: str = Field(..., description="Character ID")
    skill_name: str = Field(..., description="Skill name")
    difficulty: int = Field(..., ge=1, le=30, description="Difficulty class")
    advantage: bool = Field(False, description="Roll with advantage")
    disadvantage: bool = Field(False, description="Roll with disadvantage")
    context: Optional[str] = Field(None, description="Context for the check")


class LearnSkillRequest(BaseModel):
    """Request to learn or improve a skill."""
    session_id: str = Field(..., description="Session ID")
    character_id: str = Field(..., description="Character ID")
    skill_name: str = Field(..., description="Skill name")
    xp_gain: Optional[int] = Field(None, description="XP to add")
    instant_level: bool = Field(False, description="Instantly level up")


class UpdateLocationRequest(BaseModel):
    """Request to update character location."""
    session_id: str = Field(..., description="Session ID")
    character_id: str = Field(..., description="Character ID")
    location: Location = Field(..., description="New location")


class GetNearbyRequest(BaseModel):
    """Request to get nearby entities."""
    session_id: str = Field(..., description="Session ID")
    center: WorldCoordinates = Field(..., description="Center coordinates")
    radius: float = Field(..., gt=0, description="Search radius")
    entity_types: Optional[List[str]] = Field(None, description="Filter by entity types")


class InteractRequest(BaseModel):
    """Request to interact with an object or entity."""
    session_id: str = Field(..., description="Session ID")
    actor_id: str = Field(..., description="Actor ID")
    target_id: Optional[str] = Field(None, description="Target entity ID")
    target_location: Optional[WorldCoordinates] = Field(None, description="Target location")
    interaction_type: str = Field(..., description="Type of interaction")
    skill_check: Optional[SkillCheck] = Field(None, description="Required skill check")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Interaction data")

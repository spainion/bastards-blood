"""Pydantic models for world builder system with resources, skill areas, and crafting stations."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class ResourceType(str, Enum):
    """Types of resource nodes."""
    MINING = "mining"
    WOODCUTTING = "woodcutting"
    FISHING = "fishing"
    FARMING = "farming"
    HERB_GATHERING = "herb_gathering"
    HUNTING = "hunting"
    FORAGING = "foraging"
    QUARRYING = "quarrying"
    EXCAVATION = "excavation"
    CUSTOM = "custom"


class SkillAreaType(str, Enum):
    """Types of skill training areas."""
    TRAINING_GROUND = "training_ground"
    COMBAT_ARENA = "combat_arena"
    CRAFTING_HALL = "crafting_hall"
    MAGIC_ACADEMY = "magic_academy"
    THIEVES_GUILD = "thieves_guild"
    MONASTERY = "monastery"
    LIBRARY = "library"
    DUNGEON = "dungeon"
    WILDERNESS = "wilderness"
    CUSTOM = "custom"


class CraftingStationType(str, Enum):
    """Types of crafting stations."""
    FORGE = "forge"
    ANVIL = "anvil"
    WORKBENCH = "workbench"
    ALCHEMY_LAB = "alchemy_lab"
    ENCHANTING_TABLE = "enchanting_table"
    COOKING_STATION = "cooking_station"
    SEWING_TABLE = "sewing_table"
    FLETCHING_TABLE = "fletching_table"
    JEWELERS_BENCH = "jewelers_bench"
    TANNERY = "tannery"
    CUSTOM = "custom"


class WorldResource(BaseModel):
    """A specific resource that can be gathered."""
    resource_id: str = Field(..., description="Unique resource identifier")
    name: str = Field(..., description="Resource name")
    tier: int = Field(1, ge=1, le=10, description="Resource tier (1-10)")
    base_value: float = Field(1.0, description="Base economic value")
    stackable: bool = Field(True, description="Can multiple items stack")
    max_stack: int = Field(1000, description="Maximum stack size")


class WorldRegion(BaseModel):
    """A region in the game world."""
    id: str = Field(..., description="Region ID")
    name: str = Field(..., description="Region name")
    description: Optional[str] = Field(None, description="Region description")
    terrain_type: str = Field("plains", description="Terrain type")
    center_x: float = Field(..., description="Center X coordinate")
    center_y: float = Field(..., description="Center Y coordinate")
    center_z: float = Field(0.0, description="Center Z coordinate")
    radius: float = Field(100.0, description="Region radius")
    min_level: int = Field(1, description="Minimum recommended level")
    max_level: int = Field(120, description="Maximum recommended level")
    pvp_enabled: bool = Field(False, description="PvP allowed in this region")
    safe_zone: bool = Field(False, description="No combat allowed")
    weather: Optional[str] = Field(None, description="Current weather")
    time_of_day: Optional[str] = Field(None, description="Current time of day")


class ResourceNode(BaseModel):
    """A resource gathering point in the world."""
    id: str = Field(..., description="Node ID")
    name: str = Field(..., description="Node name")
    resource_type: ResourceType = Field(..., description="Type of resource")
    skill_required: str = Field(..., description="Skill needed to gather")
    level_required: int = Field(1, description="Skill level required")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(0.0, description="Z coordinate")
    region_id: str = Field(..., description="Parent region ID")
    resources: List[str] = Field(..., description="List of items that can be gathered")
    xp_per_gather: int = Field(10, description="XP granted per gather action")
    gather_time: float = Field(3.0, description="Time to gather in seconds")
    respawn_time: float = Field(30.0, description="Time to respawn after depletion")
    max_capacity: int = Field(100, description="Maximum resource capacity")
    current_capacity: int = Field(100, description="Current available resources")


class SkillArea(BaseModel):
    """An area dedicated to skill training."""
    id: str = Field(..., description="Area ID")
    name: str = Field(..., description="Area name")
    area_type: SkillAreaType = Field(..., description="Type of skill area")
    skills_trained: List[str] = Field(..., description="Skills that can be trained here")
    x: float = Field(..., description="Center X coordinate")
    y: float = Field(..., description="Center Y coordinate")
    z: float = Field(0.0, description="Center Z coordinate")
    radius: float = Field(50.0, description="Area radius")
    region_id: str = Field(..., description="Parent region ID")
    xp_bonus: float = Field(1.0, description="XP multiplier (1.5 = 50% bonus)")
    level_requirements: Dict[str, int] = Field(default_factory=dict, description="Level requirements per skill")
    access_cost: int = Field(0, description="Cost to access this area")
    activities: List[str] = Field(default_factory=list, description="Available activities")


class CraftingStation(BaseModel):
    """A station for crafting items."""
    id: str = Field(..., description="Station ID")
    name: str = Field(..., description="Station name")
    station_type: CraftingStationType = Field(..., description="Type of crafting station")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(0.0, description="Z coordinate")
    region_id: str = Field(..., description="Parent region ID")
    crafting_skills: List[str] = Field(..., description="Skills that can use this station")
    level_bonus: int = Field(0, description="Bonus to crafting success")
    speed_bonus: float = Field(1.0, description="Crafting speed multiplier")
    quality_bonus: int = Field(0, description="Bonus to crafted item quality")
    special_recipes: List[str] = Field(default_factory=list, description="Exclusive recipes")
    max_tier: int = Field(5, description="Maximum tier of items craftable")


class NPCZone(BaseModel):
    """A zone where NPCs spawn for combat."""
    id: str = Field(..., description="Zone ID")
    name: str = Field(..., description="Zone name")
    center_x: float = Field(..., description="Center X coordinate")
    center_y: float = Field(..., description="Center Y coordinate")
    center_z: float = Field(0.0, description="Center Z coordinate")
    radius: float = Field(100.0, description="Zone radius")
    region_id: str = Field(..., description="Parent region ID")
    npc_types: List[str] = Field(..., description="Types of NPCs that spawn")
    spawn_rate: float = Field(30.0, description="Seconds between spawns")
    max_npcs: int = Field(10, description="Maximum concurrent NPCs")
    min_level: int = Field(1, description="Minimum NPC level")
    max_level: int = Field(10, description="Maximum NPC level")
    aggressive: bool = Field(True, description="NPCs attack on sight")
    combat_xp_bonus: float = Field(1.0, description="Combat XP multiplier")
    loot_bonus: float = Field(1.0, description="Loot drop multiplier")


# Request models for admin endpoints
class CreateRegionRequest(BaseModel):
    """Request to create a new world region."""
    admin_id: str = Field(..., description="Admin creating the region")
    name: str = Field(..., description="Region name")
    description: Optional[str] = Field(None, description="Region description")
    terrain_type: str = Field("plains", description="Terrain type")
    center_x: float = Field(..., description="Center X coordinate")
    center_y: float = Field(..., description="Center Y coordinate")
    center_z: float = Field(0.0, description="Center Z coordinate")
    radius: float = Field(100.0, description="Region radius")
    min_level: Optional[int] = Field(None, description="Minimum recommended level")
    max_level: Optional[int] = Field(None, description="Maximum recommended level")
    pvp_enabled: bool = Field(False, description="Allow PvP combat")
    safe_zone: bool = Field(False, description="No combat allowed")
    weather: Optional[str] = Field(None, description="Initial weather")
    time_of_day: Optional[str] = Field(None, description="Initial time of day")
    custom_properties: Optional[Dict[str, Any]] = Field(None, description="Custom region properties")


class CreateResourceNodeRequest(BaseModel):
    """Request to create a resource node."""
    admin_id: str = Field(..., description="Admin creating the node")
    region_id: str = Field(..., description="Region to place node in")
    name: str = Field(..., description="Node name (e.g., 'Iron Ore Vein')")
    resource_type: ResourceType = Field(..., description="Type of resource")
    skill_required: str = Field(..., description="Skill needed (e.g., 'Mining')")
    level_required: Optional[int] = Field(None, description="Skill level required")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(0.0, description="Z coordinate")
    resources: List[str] = Field(..., description="Items that can be gathered")
    xp_per_gather: Optional[int] = Field(None, description="XP per gather")
    gather_time: Optional[float] = Field(None, description="Gather time in seconds")
    respawn_time: Optional[float] = Field(None, description="Respawn time in seconds")
    max_capacity: Optional[int] = Field(None, description="Max resource capacity")
    depletion_rate: Optional[int] = Field(None, description="Resources consumed per gather")
    quality_range: Optional[List[int]] = Field(None, description="Min/max quality [min, max]")
    rare_drop_chance: Optional[float] = Field(None, description="Chance for rare drop (0-1)")
    description: Optional[str] = Field(None, description="Node description")


class CreateSkillAreaRequest(BaseModel):
    """Request to create a skill training area."""
    admin_id: str = Field(..., description="Admin creating the area")
    region_id: str = Field(..., description="Region to place area in")
    name: str = Field(..., description="Area name")
    area_type: SkillAreaType = Field(..., description="Type of skill area")
    skills_trained: List[str] = Field(..., description="Skills that can be trained")
    x: float = Field(..., description="Center X coordinate")
    y: float = Field(..., description="Center Y coordinate")
    z: float = Field(0.0, description="Center Z coordinate")
    radius: Optional[float] = Field(None, description="Area radius")
    xp_bonus: Optional[float] = Field(None, description="XP multiplier")
    level_requirements: Optional[Dict[str, int]] = Field(None, description="Level requirements")
    access_cost: Optional[int] = Field(None, description="Access cost")
    activities: Optional[List[str]] = Field(None, description="Available activities")
    npcs: Optional[List[str]] = Field(None, description="NPCs in this area")
    description: Optional[str] = Field(None, description="Area description")


class CreateCraftingStationRequest(BaseModel):
    """Request to create a crafting station."""
    admin_id: str = Field(..., description="Admin creating the station")
    region_id: str = Field(..., description="Region to place station in")
    name: str = Field(..., description="Station name")
    station_type: CraftingStationType = Field(..., description="Type of crafting station")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(0.0, description="Z coordinate")
    crafting_skills: List[str] = Field(..., description="Compatible crafting skills")
    level_bonus: Optional[int] = Field(None, description="Success bonus")
    speed_bonus: Optional[float] = Field(None, description="Speed multiplier")
    quality_bonus: Optional[int] = Field(None, description="Quality bonus")
    special_recipes: Optional[List[str]] = Field(None, description="Exclusive recipes")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Usage requirements")
    usage_cost: Optional[int] = Field(None, description="Cost to use station")
    max_tier: Optional[int] = Field(None, description="Max craftable tier")
    description: Optional[str] = Field(None, description="Station description")


class CreateNPCZoneRequest(BaseModel):
    """Request to create an NPC combat zone."""
    admin_id: str = Field(..., description="Admin creating the zone")
    region_id: str = Field(..., description="Region to place zone in")
    name: str = Field(..., description="Zone name")
    center_x: float = Field(..., description="Center X coordinate")
    center_y: float = Field(..., description="Center Y coordinate")
    center_z: float = Field(0.0, description="Center Z coordinate")
    radius: Optional[float] = Field(None, description="Zone radius")
    npc_types: List[str] = Field(..., description="NPC types to spawn")
    spawn_rate: Optional[float] = Field(None, description="Spawn rate in seconds")
    max_npcs: Optional[int] = Field(None, description="Max concurrent NPCs")
    min_level: Optional[int] = Field(None, description="Min NPC level")
    max_level: Optional[int] = Field(None, description="Max NPC level")
    aggressive: bool = Field(True, description="NPCs are aggressive")
    combat_xp_bonus: Optional[float] = Field(None, description="XP multiplier")
    loot_bonus: Optional[float] = Field(None, description="Loot multiplier")
    boss_spawn_chance: Optional[float] = Field(None, description="Boss spawn chance")
    boss_templates: Optional[List[str]] = Field(None, description="Boss templates")
    description: Optional[str] = Field(None, description="Zone description")


# Request models for player actions
class GatherResourceRequest(BaseModel):
    """Request to gather resources from a node."""
    session_id: str = Field(..., description="Player session ID")
    character_id: str = Field(..., description="Character performing the action")
    node_id: str = Field(..., description="Resource node ID")


class TrainSkillRequest(BaseModel):
    """Request to train a skill in a skill area."""
    session_id: str = Field(..., description="Player session ID")
    character_id: str = Field(..., description="Character training")
    area_id: str = Field(..., description="Skill area ID")
    skill_name: str = Field(..., description="Skill to train")
    activity: Optional[str] = Field(None, description="Specific activity")


class CraftItemRequest(BaseModel):
    """Request to craft an item at a crafting station."""
    session_id: str = Field(..., description="Player session ID")
    character_id: str = Field(..., description="Character crafting")
    station_id: str = Field(..., description="Crafting station ID")
    recipe_id: str = Field(..., description="Recipe to craft")
    quantity: int = Field(1, ge=1, description="Number to craft")


class AdminWorldModifyRequest(BaseModel):
    """Request to modify world features in real-time."""
    admin_id: str = Field(..., description="Admin making the change")
    target_type: str = Field(..., description="Type of target (region, node, area, etc.)")
    target_id: str = Field(..., description="ID of target to modify")
    modifications: Dict[str, Any] = Field(..., description="Changes to apply")
    reason: Optional[str] = Field(None, description="Reason for modification")


class WorldQueryRequest(BaseModel):
    """Request to query world information."""
    query_type: str = Field(..., description="Type of query (regions, resources, etc.)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Query filters")
    limit: Optional[int] = Field(None, description="Max results")
    offset: Optional[int] = Field(None, description="Result offset for pagination")

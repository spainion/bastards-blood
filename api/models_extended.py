"""Extended Pydantic models for enhanced RPG features."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class ItemType(str, Enum):
    """Item types."""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST = "quest"
    MISC = "misc"


class ItemRarity(str, Enum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class Item(BaseModel):
    """Enhanced item model."""
    id: str = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    type: ItemType = Field(..., description="Item type")
    quantity: int = Field(1, ge=1, description="Item quantity")
    weight: Optional[float] = Field(None, description="Item weight")
    value: Optional[int] = Field(None, description="Item value in gold")
    rarity: Optional[ItemRarity] = Field(None, description="Item rarity")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom item properties")


class Resource(BaseModel):
    """Character resource (mana, stamina, etc.)."""
    max: int = Field(..., ge=0, description="Maximum value")
    current: int = Field(..., ge=0, description="Current value")


class HPStats(BaseModel):
    """Enhanced health points statistics."""
    max: int = Field(..., ge=0, description="Maximum HP")
    current: int = Field(..., ge=0, description="Current HP")
    temp: Optional[int] = Field(None, ge=0, description="Temporary HP")


class Skill(BaseModel):
    """Character skill or proficiency."""
    level: int = Field(0, ge=0, description="Skill level")
    xp: Optional[int] = Field(0, ge=0, description="Skill experience points")
    bonus: Optional[int] = Field(None, description="Skill bonus")


class AbilityType(str, Enum):
    """Ability types."""
    SPELL = "spell"
    ABILITY = "ability"
    SKILL = "skill"
    PASSIVE = "passive"


class Ability(BaseModel):
    """Special ability, spell, or power."""
    id: str = Field(..., description="Ability ID")
    name: str = Field(..., description="Ability name")
    type: AbilityType = Field(..., description="Ability type")
    cost: Optional[Dict[str, int]] = Field(default_factory=dict, description="Resource cost")
    cooldown: Optional[int] = Field(None, description="Cooldown in turns/seconds")
    description: Optional[str] = Field(None, description="Ability description")


class StatusEffectType(str, Enum):
    """Status effect types."""
    BUFF = "buff"
    DEBUFF = "debuff"
    NEUTRAL = "neutral"


class StatusEffect(BaseModel):
    """Status effect (buff, debuff)."""
    id: str = Field(..., description="Effect ID")
    name: str = Field(..., description="Effect name")
    type: StatusEffectType = Field(..., description="Effect type")
    duration: Optional[int] = Field(None, description="Duration in turns/seconds")
    stacks: int = Field(1, ge=1, description="Number of stacks")
    effects: Optional[Dict[str, int]] = Field(default_factory=dict, description="Stat modifiers")


class CraftingProfession(BaseModel):
    """Crafting profession data."""
    level: int = Field(0, ge=0, description="Profession level")
    xp: int = Field(0, ge=0, description="Profession XP")


class Crafting(BaseModel):
    """Crafting recipes and progress."""
    known_recipes: Optional[List[str]] = Field(default_factory=list, description="Known recipes")
    professions: Optional[Dict[str, CraftingProfession]] = Field(default_factory=dict, description="Profession levels")


class Appearance(BaseModel):
    """Character appearance."""
    height: Optional[str] = Field(None, description="Character height")
    weight: Optional[str] = Field(None, description="Character weight")
    hair_color: Optional[str] = Field(None, description="Hair color")
    eye_color: Optional[str] = Field(None, description="Eye color")
    skin_tone: Optional[str] = Field(None, description="Skin tone")
    age: Optional[int] = Field(None, description="Character age")


class Customization(BaseModel):
    """Character appearance and customization."""
    appearance: Optional[Appearance] = Field(None, description="Physical appearance")
    personality: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Personality traits")


class CharacterExtended(BaseModel):
    """Extended character model with inventory, equipment, crafting, etc."""
    # Core properties
    id: str = Field(..., pattern="^[a-z0-9-]+$", description="Character ID")
    name: str = Field(..., description="Character name")
    class_name: Optional[str] = Field(None, alias="class", description="Character class")
    race: Optional[str] = Field(None, description="Character race")
    lvl: Optional[int] = Field(None, ge=0, description="Character level")
    xp: Optional[int] = Field(None, ge=0, description="Experience points")
    
    # Stats and attributes
    stats: Dict[str, int] = Field(..., description="Core statistics")
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Derived/custom attributes")
    
    # Hit points and resources
    hp: HPStats = Field(..., description="Hit points")
    resources: Optional[Dict[str, Resource]] = Field(default_factory=dict, description="Character resources")
    
    # Inventory and equipment
    inventory: Optional[List[Item]] = Field(default_factory=list, description="Character inventory")
    equipment: Optional[Dict[str, Optional[Item]]] = Field(default_factory=dict, description="Equipped items")
    
    # Skills and abilities
    skills: Optional[Dict[str, Skill]] = Field(default_factory=dict, description="Character skills")
    abilities: Optional[List[Ability]] = Field(default_factory=list, description="Special abilities")
    status_effects: Optional[List[StatusEffect]] = Field(default_factory=list, description="Active status effects")
    
    # Crafting
    crafting: Optional[Crafting] = Field(None, description="Crafting data")
    
    # Currency
    currency: Optional[Dict[str, int]] = Field(default_factory=dict, description="Character currencies")
    
    # Metadata
    tags: Optional[List[str]] = Field(default_factory=list, description="Character tags")
    notes: Optional[str] = Field(None, description="Character notes")
    customization: Optional[Customization] = Field(None, description="Character customization")
    
    class Config:
        populate_by_name = True


class EquipItemRequest(BaseModel):
    """Request to equip an item."""
    character_id: str = Field(..., description="Character ID")
    item_id: str = Field(..., description="Item ID from inventory")
    slot: str = Field(..., description="Equipment slot (e.g., 'main_hand', 'chest')")


class UnequipItemRequest(BaseModel):
    """Request to unequip an item."""
    character_id: str = Field(..., description="Character ID")
    slot: str = Field(..., description="Equipment slot to clear")


class CraftItemRequest(BaseModel):
    """Request to craft an item."""
    character_id: str = Field(..., description="Character ID")
    recipe_id: str = Field(..., description="Recipe ID")
    quantity: int = Field(1, ge=1, description="Quantity to craft")


class UseItemRequest(BaseModel):
    """Request to use a consumable item."""
    character_id: str = Field(..., description="Character ID")
    item_id: str = Field(..., description="Item ID")
    target_id: Optional[str] = Field(None, description="Target character ID")


class TradeItemRequest(BaseModel):
    """Request to trade items between characters."""
    from_character_id: str = Field(..., description="Source character ID")
    to_character_id: str = Field(..., description="Target character ID")
    item_id: str = Field(..., description="Item ID")
    quantity: int = Field(1, ge=1, description="Quantity to trade")


class ApplyStatusEffectRequest(BaseModel):
    """Request to apply a status effect."""
    character_id: str = Field(..., description="Character ID")
    effect: StatusEffect = Field(..., description="Status effect to apply")


class LearnAbilityRequest(BaseModel):
    """Request to learn a new ability."""
    character_id: str = Field(..., description="Character ID")
    ability: Ability = Field(..., description="Ability to learn")


class LearnRecipeRequest(BaseModel):
    """Request to learn a crafting recipe."""
    character_id: str = Field(..., description="Character ID")
    recipe_id: str = Field(..., description="Recipe ID")


class ModifyAttributeRequest(BaseModel):
    """Request to modify a character attribute."""
    character_id: str = Field(..., description="Character ID")
    attribute: str = Field(..., description="Attribute name")
    value: Any = Field(..., description="New value")
    operation: str = Field("set", description="Operation: 'set', 'add', 'multiply'")

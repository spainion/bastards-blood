"""Pydantic models for RuneScape-style progressive skill system."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class SkillCategory(str, Enum):
    """Skill categories for organization."""
    COMBAT = "combat"
    GATHERING = "gathering"
    ARTISAN = "artisan"
    SUPPORT = "support"
    MAGIC = "magic"
    CRAFTING = "crafting"
    RESOURCE = "resource"
    SOCIAL = "social"


class RuneScapeSkill(BaseModel):
    """
    RuneScape-style skill with progressive leveling (1-99+).
    
    Features:
    - Exponential XP requirements per level
    - Skills impact rolls, success rates, and unlocks
    - Access to tier-gated content (bronze -> iron -> steel -> mithril -> adamant -> rune -> dragon)
    """
    name: str = Field(..., description="Skill name")
    level: int = Field(1, ge=1, le=120, description="Current skill level (1-120)")
    xp: int = Field(0, ge=0, description="Total XP earned in this skill")
    category: SkillCategory = Field(..., description="Skill category")
    base_attribute: Optional[str] = Field(None, description="Base attribute (STR, DEX, etc.)")
    description: Optional[str] = Field(None, description="Skill description")
    
    @property
    def xp_to_next_level(self) -> int:
        """Calculate XP needed for next level using RuneScape formula."""
        if self.level >= 120:
            return 0
        return self.calculate_xp_for_level(self.level + 1) - self.xp
    
    @property
    def xp_for_current_level(self) -> int:
        """XP required to reach current level."""
        return self.calculate_xp_for_level(self.level)
    
    @property
    def progress_to_next(self) -> float:
        """Progress percentage to next level (0.0-1.0)."""
        if self.level >= 120:
            return 1.0
        current_level_xp = self.calculate_xp_for_level(self.level)
        next_level_xp = self.calculate_xp_for_level(self.level + 1)
        xp_in_level = self.xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        return xp_in_level / xp_needed if xp_needed > 0 else 0.0
    
    @staticmethod
    def calculate_xp_for_level(level: int) -> int:
        """
        Calculate total XP required for a level using RuneScape formula.
        Formula: sum from 1 to (level-1) of floor(level + 300 * 2^(level/7)) / 4
        """
        if level <= 1:
            return 0
        
        total_xp = 0
        for lvl in range(1, level):
            total_xp += int((lvl + 300 * (2 ** (lvl / 7.0))) / 4)
        return total_xp
    
    @property
    def tier(self) -> str:
        """Get equipment/resource tier based on level."""
        if self.level >= 90:
            return "dragon"
        elif self.level >= 70:
            return "adamant"
        elif self.level >= 50:
            return "mithril"
        elif self.level >= 30:
            return "steel"
        elif self.level >= 15:
            return "iron"
        else:
            return "bronze"
    
    @property
    def bonus(self) -> int:
        """Bonus modifier based on level (for skill checks)."""
        # Each 10 levels gives +1 bonus, max +12 at level 120
        return self.level // 10
    
    def can_access_tier(self, required_level: int) -> bool:
        """Check if character can access content of given level requirement."""
        return self.level >= required_level
    
    def success_multiplier(self) -> float:
        """Success rate multiplier based on level (1.0 at level 1, 2.0 at level 99)."""
        return 1.0 + (self.level - 1) / 99.0


class SkillTier(BaseModel):
    """Tier definition for equipment, resources, or content."""
    name: str = Field(..., description="Tier name (bronze, iron, steel, etc.)")
    level_required: int = Field(..., ge=1, le=120, description="Level required to access")
    color: Optional[str] = Field(None, description="Tier color code")
    multiplier: float = Field(1.0, description="Effectiveness multiplier")
    description: Optional[str] = Field(None, description="Tier description")


class SkillRequirement(BaseModel):
    """Skill requirement for an action, item, or content."""
    skill_name: str = Field(..., description="Required skill name")
    level_required: int = Field(..., ge=1, le=120, description="Minimum level required")
    optional: bool = Field(False, description="Whether requirement is optional")


class SkillXPGain(BaseModel):
    """XP gain event for a skill."""
    skill_name: str = Field(..., description="Skill name")
    xp_gained: int = Field(..., gt=0, description="XP amount gained")
    reason: Optional[str] = Field(None, description="Reason for XP gain")
    base_xp: Optional[int] = Field(None, description="Base XP before multipliers")
    multiplier: float = Field(1.0, description="XP multiplier applied")


class SkillAction(BaseModel):
    """Action that trains a skill."""
    skill_name: str = Field(..., description="Skill being trained")
    action_name: str = Field(..., description="Action name")
    base_xp: int = Field(..., gt=0, description="Base XP reward")
    level_required: int = Field(1, ge=1, le=120, description="Level required to perform")
    success_rate_base: float = Field(1.0, ge=0, le=1, description="Base success rate")
    duration: float = Field(1.0, gt=0, description="Action duration in seconds")
    resources_required: Optional[Dict[str, int]] = Field(None, description="Resources needed")
    products: Optional[List[Dict[str, Any]]] = Field(None, description="Items produced")


class ProgressiveCheck(BaseModel):
    """
    Progressive skill check that scales with level.
    Higher levels increase success rate and reduce failure penalties.
    """
    skill_name: str = Field(..., description="Skill being checked")
    difficulty: int = Field(..., ge=1, le=120, description="Difficulty level")
    character_level: int = Field(..., ge=1, le=120, description="Character's skill level")
    roll: Optional[int] = Field(None, description="Random roll (if used)")
    success: bool = Field(..., description="Whether check succeeded")
    margin: int = Field(..., description="Margin of success/failure")
    critical_success: bool = Field(False, description="Critical success")
    critical_failure: bool = Field(False, description="Critical failure")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate based on level vs difficulty."""
        # Base 50% at equal level, +5% per level difference
        level_diff = self.character_level - self.difficulty
        rate = 0.5 + (level_diff * 0.05)
        # Clamp between 5% and 95%
        return max(0.05, min(0.95, rate))


class SkillUnlock(BaseModel):
    """Content unlocked at a skill level."""
    skill_name: str = Field(..., description="Skill name")
    level: int = Field(..., ge=1, le=120, description="Level unlocked at")
    unlock_type: str = Field(..., description="Type of unlock (item, recipe, location, ability)")
    unlock_id: str = Field(..., description="ID of unlocked content")
    name: str = Field(..., description="Name of unlocked content")
    description: Optional[str] = Field(None, description="Description")


class CharacterSkills(BaseModel):
    """Complete skill profile for a character."""
    character_id: str = Field(..., description="Character ID")
    skills: Dict[str, RuneScapeSkill] = Field(default_factory=dict, description="Skill name -> skill data")
    total_level: Optional[int] = Field(None, description="Sum of all skill levels")
    combat_level: Optional[int] = Field(None, description="Combat level calculation")
    
    def get_skill(self, skill_name: str) -> Optional[RuneScapeSkill]:
        """Get skill by name."""
        return self.skills.get(skill_name)
    
    def calculate_total_level(self) -> int:
        """Calculate total level (sum of all skills)."""
        return sum(skill.level for skill in self.skills.values())
    
    def calculate_combat_level(self) -> int:
        """
        Calculate combat level based on combat skills.
        RuneScape formula: base 3 + (Attack + Strength) * 0.325 + (Defence + Hitpoints) * 0.325
        """
        combat_skills = ["Attack", "Strength", "Defence", "Hitpoints", "Magic", "Ranged", "Prayer"]
        combat_stats = {name: self.skills.get(name, RuneScapeSkill(name=name, level=1, xp=0, category=SkillCategory.COMBAT))
                       for name in combat_skills}
        
        attack = combat_stats.get("Attack", RuneScapeSkill(name="Attack", level=1, xp=0, category=SkillCategory.COMBAT)).level
        strength = combat_stats.get("Strength", RuneScapeSkill(name="Strength", level=1, xp=0, category=SkillCategory.COMBAT)).level
        defence = combat_stats.get("Defence", RuneScapeSkill(name="Defence", level=1, xp=0, category=SkillCategory.COMBAT)).level
        hitpoints = combat_stats.get("Hitpoints", RuneScapeSkill(name="Hitpoints", level=10, xp=1154, category=SkillCategory.COMBAT)).level
        magic = combat_stats.get("Magic", RuneScapeSkill(name="Magic", level=1, xp=0, category=SkillCategory.MAGIC)).level
        ranged = combat_stats.get("Ranged", RuneScapeSkill(name="Ranged", level=1, xp=0, category=SkillCategory.COMBAT)).level
        prayer = combat_stats.get("Prayer", RuneScapeSkill(name="Prayer", level=1, xp=0, category=SkillCategory.SUPPORT)).level
        
        # Calculate combat level
        base = 0.25 * (defence + hitpoints + int(prayer / 2))
        melee = 0.325 * (attack + strength)
        ranged_calc = 0.325 * (int(ranged / 2) + ranged)
        magic_calc = 0.325 * (int(magic / 2) + magic)
        
        combat_level = base + max(melee, ranged_calc, magic_calc)
        return int(combat_level)


# API Request/Response Models

class AddSkillXPRequest(BaseModel):
    """Request to add XP to a skill."""
    session_id: str = Field(..., description="Session ID")
    character_id: str = Field(..., description="Character ID")
    skill_name: str = Field(..., description="Skill name")
    xp_amount: int = Field(..., gt=0, description="XP to add")
    reason: Optional[str] = Field(None, description="Reason for XP gain")


class PerformSkillActionRequest(BaseModel):
    """Request to perform an action that trains a skill."""
    session_id: str = Field(..., description="Session ID")
    character_id: str = Field(..., description="Character ID")
    skill_name: str = Field(..., description="Skill name")
    action_name: str = Field(..., description="Action to perform")
    quantity: int = Field(1, ge=1, description="How many times to perform action")


class CheckSkillRequirementRequest(BaseModel):
    """Request to check if character meets skill requirements."""
    character_id: str = Field(..., description="Character ID")
    requirements: List[SkillRequirement] = Field(..., description="Skill requirements to check")


class ProgressiveCheckRequest(BaseModel):
    """Request to perform a progressive skill check."""
    session_id: str = Field(..., description="Session ID")
    character_id: str = Field(..., description="Character ID")
    skill_name: str = Field(..., description="Skill to check")
    difficulty: int = Field(..., ge=1, le=120, description="Difficulty level (1-120)")
    use_random: bool = Field(True, description="Include random element")


class GetSkillInfoRequest(BaseModel):
    """Request to get skill information."""
    character_id: str = Field(..., description="Character ID")
    skill_name: Optional[str] = Field(None, description="Specific skill (or all if None)")


class SkillActionResponse(BaseModel):
    """Response for skill action."""
    success: bool = Field(..., description="Whether action succeeded")
    xp_gained: int = Field(0, description="XP gained")
    level_ups: List[Dict[str, Any]] = Field(default_factory=list, description="Level ups achieved")
    items_produced: List[Dict[str, Any]] = Field(default_factory=list, description="Items created")
    new_level: int = Field(..., description="New skill level")
    new_xp: int = Field(..., description="New total XP")
    message: Optional[str] = Field(None, description="Result message")


class SkillsOverviewResponse(BaseModel):
    """Overview of character's skills."""
    character_id: str = Field(..., description="Character ID")
    skills: List[Dict[str, Any]] = Field(..., description="All skills")
    total_level: int = Field(..., description="Total level")
    combat_level: int = Field(..., description="Combat level")
    unlocks: List[SkillUnlock] = Field(default_factory=list, description="Recent unlocks")

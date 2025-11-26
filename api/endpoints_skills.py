"""API endpoints for RuneScape-style progressive skill system."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import random

from .auth import verify_api_key
from .models import ActionResponse
from .models_skills import (
    RuneScapeSkill, SkillCategory, CharacterSkills, SkillTier,
    SkillRequirement, SkillXPGain, SkillAction, ProgressiveCheck,
    SkillUnlock, AddSkillXPRequest, PerformSkillActionRequest,
    CheckSkillRequirementRequest, ProgressiveCheckRequest,
    GetSkillInfoRequest, SkillActionResponse, SkillsOverviewResponse
)
from .data_manager import data_manager

# Create router for skills endpoints
router = APIRouter(prefix="/api/v1/skills", tags=["Skills System"], dependencies=[Depends(verify_api_key)])


# Default RuneScape skill definitions
DEFAULT_SKILLS = {
    # Combat Skills
    "Attack": SkillCategory.COMBAT,
    "Strength": SkillCategory.COMBAT,
    "Defence": SkillCategory.COMBAT,
    "Ranged": SkillCategory.COMBAT,
    "Magic": SkillCategory.MAGIC,
    "Hitpoints": SkillCategory.COMBAT,
    "Prayer": SkillCategory.SUPPORT,
    
    # Gathering Skills
    "Mining": SkillCategory.GATHERING,
    "Fishing": SkillCategory.GATHERING,
    "Woodcutting": SkillCategory.GATHERING,
    "Hunter": SkillCategory.GATHERING,
    "Farming": SkillCategory.GATHERING,
    
    # Artisan Skills
    "Smithing": SkillCategory.ARTISAN,
    "Crafting": SkillCategory.CRAFTING,
    "Fletching": SkillCategory.CRAFTING,
    "Cooking": SkillCategory.ARTISAN,
    "Firemaking": SkillCategory.ARTISAN,
    "Herblore": SkillCategory.CRAFTING,
    "Runecrafting": SkillCategory.MAGIC,
    "Construction": SkillCategory.ARTISAN,
    
    # Support Skills
    "Agility": SkillCategory.SUPPORT,
    "Thieving": SkillCategory.SUPPORT,
    "Slayer": SkillCategory.COMBAT,
    "Summoning": SkillCategory.MAGIC,
    "Dungeoneering": SkillCategory.SUPPORT,
}


# Tier definitions
TIERS = [
    SkillTier(name="bronze", level_required=1, color="#CD7F32", multiplier=1.0),
    SkillTier(name="iron", level_required=15, color="#C0C0C0", multiplier=1.2),
    SkillTier(name="steel", level_required=30, color="#808080", multiplier=1.4),
    SkillTier(name="mithril", level_required=50, color="#0000FF", multiplier=1.6),
    SkillTier(name="adamant", level_required=70, color="#00FF00", multiplier=1.8),
    SkillTier(name="rune", level_required=90, color="#00FFFF", multiplier=2.0),
    SkillTier(name="dragon", level_required=99, color="#FF0000", multiplier=2.5),
]


def _get_or_create_character_skills(character_id: str) -> CharacterSkills:
    """Get character skills or initialize defaults."""
    char_data = data_manager.load_character(character_id)
    if not char_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found"
        )
    
    # Get existing skills or create defaults
    skills_data = char_data.get("skills_progressive", {})
    skills = {}
    
    for skill_name, category in DEFAULT_SKILLS.items():
        if skill_name in skills_data:
            skill_dict = skills_data[skill_name]
            skills[skill_name] = RuneScapeSkill(
                name=skill_name,
                level=skill_dict.get("level", 1),
                xp=skill_dict.get("xp", 0),
                category=category,
                description=skill_dict.get("description")
            )
        else:
            # Hitpoints starts at level 10
            start_level = 10 if skill_name == "Hitpoints" else 1
            start_xp = RuneScapeSkill.calculate_xp_for_level(start_level) if start_level > 1 else 0
            skills[skill_name] = RuneScapeSkill(
                name=skill_name,
                level=start_level,
                xp=start_xp,
                category=category
            )
    
    return CharacterSkills(character_id=character_id, skills=skills)


def _save_character_skills(char_skills: CharacterSkills):
    """Save character skills back to storage."""
    char_data = data_manager.load_character(char_skills.character_id)
    if not char_data:
        return
    
    # Convert skills to dict format
    skills_dict = {}
    for skill_name, skill in char_skills.skills.items():
        skills_dict[skill_name] = {
            "name": skill.name,
            "level": skill.level,
            "xp": skill.xp,
            "category": skill.category.value,
            "tier": skill.tier,
            "bonus": skill.bonus,
            "xp_to_next": skill.xp_to_next_level,
            "progress": skill.progress_to_next
        }
    
    char_data["skills_progressive"] = skills_dict
    char_data["total_level"] = char_skills.calculate_total_level()
    char_data["combat_level"] = char_skills.calculate_combat_level()
    
    data_manager.save_character(char_skills.character_id, char_data)


@router.get("/overview", response_model=SkillsOverviewResponse)
async def get_skills_overview(character_id: str) -> SkillsOverviewResponse:
    """Get overview of all character skills."""
    char_skills = _get_or_create_character_skills(character_id)
    
    skills_list = []
    for skill_name, skill in char_skills.skills.items():
        skills_list.append({
            "name": skill.name,
            "level": skill.level,
            "xp": skill.xp,
            "xp_to_next": skill.xp_to_next_level,
            "progress": skill.progress_to_next,
            "category": skill.category.value,
            "tier": skill.tier,
            "bonus": skill.bonus
        })
    
    # Sort by level descending
    skills_list.sort(key=lambda x: x["level"], reverse=True)
    
    return SkillsOverviewResponse(
        character_id=character_id,
        skills=skills_list,
        total_level=char_skills.calculate_total_level(),
        combat_level=char_skills.calculate_combat_level(),
        unlocks=[]
    )


@router.get("/skill/{skill_name}", response_model=Dict[str, Any])
async def get_skill_details(character_id: str, skill_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific skill."""
    char_skills = _get_or_create_character_skills(character_id)
    
    skill = char_skills.get_skill(skill_name)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {skill_name} not found"
        )
    
    # Get available tiers
    accessible_tiers = [tier for tier in TIERS if skill.level >= tier.level_required]
    next_tier = next((tier for tier in TIERS if skill.level < tier.level_required), None)
    
    return {
        "name": skill.name,
        "level": skill.level,
        "xp": skill.xp,
        "xp_to_next": skill.xp_to_next_level,
        "progress_percent": round(skill.progress_to_next * 100, 2),
        "category": skill.category.value,
        "current_tier": skill.tier,
        "accessible_tiers": [tier.dict() for tier in accessible_tiers],
        "next_tier": next_tier.dict() if next_tier else None,
        "bonus": skill.bonus,
        "success_multiplier": skill.success_multiplier()
    }


@router.post("/add-xp", response_model=SkillActionResponse)
async def add_skill_xp(request: AddSkillXPRequest) -> SkillActionResponse:
    """
    Add XP to a skill and handle level-ups.
    Returns new level, XP, and any level-ups achieved.
    """
    # Verify session
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Get character skills
    char_skills = _get_or_create_character_skills(request.character_id)
    skill = char_skills.get_skill(request.skill_name)
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {request.skill_name} not found"
        )
    
    # Store old level
    old_level = skill.level
    old_xp = skill.xp
    
    # Add XP
    skill.xp += request.xp_amount
    
    # Check for level ups
    level_ups = []
    while skill.level < 120 and skill.xp >= RuneScapeSkill.calculate_xp_for_level(skill.level + 1):
        skill.level += 1
        level_ups.append({
            "skill": skill.name,
            "new_level": skill.level,
            "tier": skill.tier,
            "bonus": skill.bonus
        })
    
    # Save updated skills
    _save_character_skills(char_skills)
    
    # Create event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "skill_xp_gained",
        "actor": request.character_id,
        "data": {
            "skill_name": request.skill_name,
            "xp_gained": request.xp_amount,
            "old_level": old_level,
            "new_level": skill.level,
            "old_xp": old_xp,
            "new_xp": skill.xp,
            "level_ups": level_ups,
            "reason": request.reason
        }
    }
    data_manager.add_event(request.session_id, event)
    
    # Create level up events
    for level_up in level_ups:
        event_id = data_manager.generate_event_id()
        event = {
            "id": event_id,
            "ts": datetime.now(timezone.utc).isoformat() + 'Z',
            "t": "skill_level_up",
            "actor": request.character_id,
            "data": level_up
        }
        data_manager.add_event(request.session_id, event)
    
    message = f"Gained {request.xp_amount} XP in {request.skill_name}"
    if level_ups:
        levels_str = ", ".join([f"Level {lu['new_level']}" for lu in level_ups])
        message += f". Level up! {levels_str}"
    
    return SkillActionResponse(
        success=True,
        xp_gained=request.xp_amount,
        level_ups=level_ups,
        items_produced=[],
        new_level=skill.level,
        new_xp=skill.xp,
        message=message
    )


@router.post("/progressive-check", response_model=ActionResponse)
async def perform_progressive_check(request: ProgressiveCheckRequest) -> ActionResponse:
    """
    Perform a progressive skill check where success rate scales with level.
    Higher levels increase success chance and quality of results.
    """
    # Verify session
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Get character skills
    char_skills = _get_or_create_character_skills(request.character_id)
    skill = char_skills.get_skill(request.skill_name)
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {request.skill_name} not found"
        )
    
    # Calculate success rate
    level_diff = skill.level - request.difficulty
    base_success_rate = 0.5 + (level_diff * 0.05)
    success_rate = max(0.05, min(0.95, base_success_rate))
    
    # Perform check
    roll = random.random() if request.use_random else 0.75
    success = roll < success_rate
    margin = int((success_rate - roll) * 100)
    
    # Check for criticals (5% chance each)
    critical_success = roll < 0.05 and success
    critical_failure = roll > 0.95 and not success
    
    # Create check object
    check = ProgressiveCheck(
        skill_name=request.skill_name,
        difficulty=request.difficulty,
        character_level=skill.level,
        roll=int(roll * 100),
        success=success,
        margin=margin,
        critical_success=critical_success,
        critical_failure=critical_failure
    )
    
    # Create event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "progressive_skill_check",
        "actor": request.character_id,
        "data": {
            "skill_name": request.skill_name,
            "difficulty": request.difficulty,
            "character_level": skill.level,
            "success_rate": round(success_rate * 100, 2),
            "roll": check.roll,
            "success": success,
            "margin": margin,
            "critical_success": critical_success,
            "critical_failure": critical_failure
        }
    }
    data_manager.add_event(request.session_id, event)
    
    result_msg = "Success" if success else "Failure"
    if critical_success:
        result_msg = "Critical Success!"
    elif critical_failure:
        result_msg = "Critical Failure!"
    
    return ActionResponse(
        success=success,
        message=f"{request.skill_name} check (Lvl {skill.level} vs DC {request.difficulty}): {result_msg}",
        data={
            "check": check.dict(),
            "success_rate_percent": round(success_rate * 100, 2),
            "tier": skill.tier,
            "bonus": skill.bonus
        }
    )


@router.post("/check-requirements", response_model=ActionResponse)
async def check_skill_requirements(request: CheckSkillRequirementRequest) -> ActionResponse:
    """Check if character meets skill requirements."""
    char_skills = _get_or_create_character_skills(request.character_id)
    
    results = []
    all_met = True
    
    for req in request.requirements:
        skill = char_skills.get_skill(req.skill_name)
        if not skill:
            results.append({
                "skill": req.skill_name,
                "required": req.level_required,
                "current": 0,
                "met": False,
                "optional": req.optional
            })
            if not req.optional:
                all_met = False
            continue
        
        met = skill.level >= req.level_required
        results.append({
            "skill": req.skill_name,
            "required": req.level_required,
            "current": skill.level,
            "met": met,
            "optional": req.optional
        })
        
        if not met and not req.optional:
            all_met = False
    
    return ActionResponse(
        success=all_met,
        message="All requirements met" if all_met else "Some requirements not met",
        data={"requirements": results}
    )


@router.get("/tiers", response_model=List[Dict[str, Any]])
async def get_tiers() -> List[Dict[str, Any]]:
    """Get list of all equipment/resource tiers."""
    return [tier.dict() for tier in TIERS]


@router.get("/available-skills", response_model=List[Dict[str, str]])
async def get_available_skills() -> List[Dict[str, str]]:
    """Get list of all available skills and their categories."""
    return [
        {"name": name, "category": category.value}
        for name, category in DEFAULT_SKILLS.items()
    ]


@router.post("/perform-action", response_model=SkillActionResponse)
async def perform_skill_action(request: PerformSkillActionRequest) -> SkillActionResponse:
    """
    Perform an action that trains a skill (e.g., mine ore, cut tree, smith item).
    Success depends on skill level vs action difficulty.
    """
    # Verify session
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Get character skills
    char_skills = _get_or_create_character_skills(request.character_id)
    skill = char_skills.get_skill(request.skill_name)
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {request.skill_name} not found"
        )
    
    # Define some example actions
    skill_actions = {
        "Mining": {
            "mine_copper": SkillAction(skill_name="Mining", action_name="mine_copper", base_xp=17, level_required=1, success_rate_base=0.8, duration=3.0),
            "mine_iron": SkillAction(skill_name="Mining", action_name="mine_iron", base_xp=35, level_required=15, success_rate_base=0.6, duration=4.0),
            "mine_mithril": SkillAction(skill_name="Mining", action_name="mine_mithril", base_xp=80, level_required=55, success_rate_base=0.5, duration=6.0),
        },
        "Woodcutting": {
            "cut_tree": SkillAction(skill_name="Woodcutting", action_name="cut_tree", base_xp=25, level_required=1, success_rate_base=0.8, duration=4.0),
            "cut_oak": SkillAction(skill_name="Woodcutting", action_name="cut_oak", base_xp=37, level_required=15, success_rate_base=0.7, duration=5.0),
            "cut_magic": SkillAction(skill_name="Woodcutting", action_name="cut_magic", base_xp=250, level_required=75, success_rate_base=0.4, duration=10.0),
        },
        "Fishing": {
            "catch_shrimp": SkillAction(skill_name="Fishing", action_name="catch_shrimp", base_xp=10, level_required=1, success_rate_base=0.9, duration=2.0),
            "catch_salmon": SkillAction(skill_name="Fishing", action_name="catch_salmon", base_xp=50, level_required=30, success_rate_base=0.6, duration=5.0),
            "catch_shark": SkillAction(skill_name="Fishing", action_name="catch_shark", base_xp=110, level_required=76, success_rate_base=0.3, duration=8.0),
        }
    }
    
    # Get action
    actions = skill_actions.get(request.skill_name, {})
    action = actions.get(request.action_name)
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action {request.action_name} not found for skill {request.skill_name}"
        )
    
    # Check level requirement
    if skill.level < action.level_required:
        return SkillActionResponse(
            success=False,
            xp_gained=0,
            level_ups=[],
            items_produced=[],
            new_level=skill.level,
            new_xp=skill.xp,
            message=f"Level {action.level_required} {request.skill_name} required (you are level {skill.level})"
        )
    
    # Calculate success rate
    level_diff = skill.level - action.level_required
    success_rate = min(0.95, action.success_rate_base + (level_diff * 0.02))
    
    # Perform actions
    successes = 0
    total_xp = 0
    items = []
    level_ups = []
    old_level = skill.level
    
    for _ in range(request.quantity):
        if random.random() < success_rate:
            successes += 1
            total_xp += action.base_xp
            items.append({"name": action.action_name.replace("_", " ").title(), "quantity": 1})
    
    # Add XP and check level ups
    if total_xp > 0:
        old_xp = skill.xp
        skill.xp += total_xp
        
        while skill.level < 120 and skill.xp >= RuneScapeSkill.calculate_xp_for_level(skill.level + 1):
            skill.level += 1
            level_ups.append({
                "skill": skill.name,
                "new_level": skill.level,
                "tier": skill.tier,
                "bonus": skill.bonus
            })
        
        _save_character_skills(char_skills)
        
        # Create event
        event_id = data_manager.generate_event_id()
        event = {
            "id": event_id,
            "ts": datetime.now(timezone.utc).isoformat() + 'Z',
            "t": "skill_action_performed",
            "actor": request.character_id,
            "data": {
                "skill_name": request.skill_name,
                "action_name": request.action_name,
                "quantity": request.quantity,
                "successes": successes,
                "xp_gained": total_xp,
                "items_produced": items,
                "old_level": old_level,
                "new_level": skill.level,
                "level_ups": level_ups
            }
        }
        data_manager.add_event(request.session_id, event)
    
    message = f"Performed {request.action_name} {successes}/{request.quantity} times. Gained {total_xp} XP."
    if level_ups:
        message += f" Level up! Now level {skill.level}."
    
    return SkillActionResponse(
        success=successes > 0,
        xp_gained=total_xp,
        level_ups=level_ups,
        items_produced=items,
        new_level=skill.level,
        new_xp=skill.xp,
        message=message
    )

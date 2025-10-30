"""API endpoints for world coordinates, movement, actions, and skills."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import random
import math

from .auth import verify_api_key
from .models import ActionResponse
from .models_world import (
    WorldCoordinates, Location, MovementAction, MovementType,
    Skill, SkillCheck, GameAction, ActionType, Zone,
    MoveCharacterRequest, TeleportRequest, SkillCheckRequest,
    LearnSkillRequest, UpdateLocationRequest, GetNearbyRequest,
    InteractRequest, PathfindingRequest, TerrainType
)
from .data_manager import data_manager

# Create router for world/movement endpoints
router = APIRouter(prefix="/api/v1/world", tags=["World & Movement"], dependencies=[Depends(verify_api_key)])


@router.post("/move", response_model=ActionResponse)
async def move_character(request: MoveCharacterRequest) -> ActionResponse:
    """
    Move a character to a new location.
    Calculates distance, duration, and stamina cost based on movement type.
    """
    # Verify session exists
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Load character to get current location
    char_data = data_manager.load_character(request.character_id)
    if not char_data:
        # Try loading as NPC
        char_data = data_manager.load_npc(request.character_id)
        if not char_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character/NPC {request.character_id} not found"
            )
    
    # Get current location or use default
    current_loc = char_data.get("location", {})
    from_coords = WorldCoordinates(
        x=current_loc.get("position", {}).get("x", 0),
        y=current_loc.get("position", {}).get("y", 0),
        z=current_loc.get("position", {}).get("z", 0),
        region=current_loc.get("area", "unknown")
    )
    
    # Calculate distance
    distance = from_coords.distance_to(request.destination)
    
    # Calculate duration based on movement type and distance
    speed_multipliers = {
        MovementType.WALK: 1.0,
        MovementType.RUN: 2.0,
        MovementType.SPRINT: 3.0,
        MovementType.SNEAK: 0.5,
        MovementType.CRAWL: 0.25,
        MovementType.SWIM: 0.8,
        MovementType.FLY: 2.5,
        MovementType.CLIMB: 0.6,
        MovementType.JUMP: 1.5
    }
    
    base_speed = 30.0  # Base speed units per second
    actual_speed = base_speed * speed_multipliers.get(request.movement_type, 1.0)
    duration = distance / actual_speed if actual_speed > 0 else 0
    
    # Calculate stamina cost
    stamina_costs = {
        MovementType.WALK: 0.1,
        MovementType.RUN: 0.3,
        MovementType.SPRINT: 0.6,
        MovementType.SNEAK: 0.15,
        MovementType.CRAWL: 0.2,
        MovementType.SWIM: 0.4,
        MovementType.FLY: 0.5,
        MovementType.CLIMB: 0.5,
        MovementType.JUMP: 0.3
    }
    
    stamina_cost = distance * stamina_costs.get(request.movement_type, 0.1)
    
    # Create movement event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "character_move",
        "actor": request.character_id,
        "data": {
            "movement_type": request.movement_type.value,
            "from": {
                "x": from_coords.x,
                "y": from_coords.y,
                "z": from_coords.z,
                "region": from_coords.region
            },
            "to": {
                "x": request.destination.x,
                "y": request.destination.y,
                "z": request.destination.z,
                "region": request.destination.region
            },
            "distance": round(distance, 2),
            "duration": round(duration, 2),
            "stamina_cost": round(stamina_cost, 2)
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Moved {distance:.2f} units via {request.movement_type.value}",
        result={
            "distance": round(distance, 2),
            "duration": round(duration, 2),
            "stamina_cost": round(stamina_cost, 2),
            "destination": request.destination.model_dump()
        }
    )


@router.post("/teleport", response_model=ActionResponse)
async def teleport_character(request: TeleportRequest) -> ActionResponse:
    """
    Instantly teleport a character to a new location.
    No travel time or stamina cost.
    """
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Create teleport event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "character_teleport",
        "actor": request.character_id,
        "data": {
            "destination": {
                "x": request.destination.x,
                "y": request.destination.y,
                "z": request.destination.z,
                "region": request.destination.region,
                "area": request.destination.area
            },
            "reason": request.reason
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Teleported to ({request.destination.x}, {request.destination.y}, {request.destination.z})",
        result={"destination": request.destination.model_dump()}
    )


@router.post("/skill-check", response_model=ActionResponse)
async def perform_skill_check(request: SkillCheckRequest) -> ActionResponse:
    """
    Perform a skill check with D20 roll mechanics.
    Supports advantage and disadvantage.
    """
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Load character to get skill bonuses
    char_data = data_manager.load_character(request.character_id)
    if not char_data:
        char_data = data_manager.load_npc(request.character_id)
        if not char_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {request.character_id} not found"
            )
    
    # Get skill modifier
    skills = char_data.get("skills", {})
    skill_data = skills.get(request.skill_name, {})
    skill_level = skill_data.get("level", 0) if isinstance(skill_data, dict) else 0
    skill_bonus = skill_data.get("bonus", 0) if isinstance(skill_data, dict) else 0
    modifier = skill_level + skill_bonus
    
    # Roll D20
    if request.advantage:
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        roll = max(roll1, roll2)
        roll_text = f"Advantage: {roll1}, {roll2} -> {roll}"
    elif request.disadvantage:
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        roll = min(roll1, roll2)
        roll_text = f"Disadvantage: {roll1}, {roll2} -> {roll}"
    else:
        roll = random.randint(1, 20)
        roll_text = str(roll)
    
    total = roll + modifier
    success = total >= request.difficulty
    critical = roll == 20
    critical_fail = roll == 1
    
    # Create skill check event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "skill_check",
        "actor": request.character_id,
        "data": {
            "skill": request.skill_name,
            "difficulty": request.difficulty,
            "roll": roll,
            "modifier": modifier,
            "total": total,
            "success": success,
            "critical": critical,
            "critical_fail": critical_fail,
            "roll_text": roll_text,
            "context": request.context
        },
        "result": {"success": success}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    result_text = "Success!" if success else "Failed!"
    if critical:
        result_text = "Critical Success!"
    elif critical_fail:
        result_text = "Critical Failure!"
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"{request.skill_name} check: {roll_text} + {modifier} = {total} vs DC {request.difficulty} - {result_text}",
        result={
            "roll": roll,
            "modifier": modifier,
            "total": total,
            "difficulty": request.difficulty,
            "success": success,
            "critical": critical,
            "critical_fail": critical_fail
        }
    )


@router.post("/learn-skill", response_model=ActionResponse)
async def learn_skill(request: LearnSkillRequest) -> ActionResponse:
    """
    Learn a new skill or add XP to existing skill.
    Automatically levels up skill when enough XP is gained.
    """
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Load character
    char_data = data_manager.load_character(request.character_id)
    if not char_data:
        char_data = data_manager.load_npc(request.character_id)
        if not char_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {request.character_id} not found"
            )
    
    # Get current skill data
    skills = char_data.get("skills", {})
    skill_data = skills.get(request.skill_name, {"level": 0, "xp": 0})
    
    current_level = skill_data.get("level", 0)
    current_xp = skill_data.get("xp", 0)
    
    # Add XP or instant level
    if request.instant_level:
        new_level = current_level + 1
        new_xp = 0
        level_up = True
    else:
        xp_to_add = request.xp_gain or 100
        new_xp = current_xp + xp_to_add
        
        # Calculate if level up (100 XP per level)
        xp_per_level = 100
        new_level = current_level
        level_up = False
        
        while new_xp >= xp_per_level:
            new_xp -= xp_per_level
            new_level += 1
            level_up = True
            xp_per_level = 100 + (new_level * 10)  # Increasing XP requirement
    
    # Create skill learn/level event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "skill_learn" if current_level == 0 else "skill_level_up" if level_up else "skill_xp_gain",
        "actor": request.character_id,
        "data": {
            "skill": request.skill_name,
            "old_level": current_level,
            "new_level": new_level,
            "xp_gained": request.xp_gain,
            "new_xp": new_xp,
            "level_up": level_up
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    message = f"Learned skill: {request.skill_name}" if current_level == 0 else \
              f"Leveled up {request.skill_name} to level {new_level}!" if level_up else \
              f"Gained {request.xp_gain} XP in {request.skill_name}"
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=message,
        result={
            "skill": request.skill_name,
            "level": new_level,
            "xp": new_xp,
            "level_up": level_up
        }
    )


@router.post("/action", response_model=ActionResponse)
async def perform_action(request: GameAction) -> ActionResponse:
    """
    Perform a general game action (interact, examine, search, etc.).
    Can include skill checks and resource costs.
    """
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Perform skill check if required
    skill_check_result = None
    if request.skill_check:
        roll = random.randint(1, 20)
        total = roll + (request.skill_check.modifier or 0)
        success = total >= request.skill_check.difficulty
        skill_check_result = {
            "roll": roll,
            "total": total,
            "success": success
        }
    
    # Create action event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": f"action_{request.action_type.value}",
        "actor": request.actor_id,
        "target": request.target_id,
        "data": {
            "action_type": request.action_type.value,
            "target_location": request.target_location.model_dump() if request.target_location else None,
            "duration": request.duration,
            "cost": request.cost,
            "skill_check": skill_check_result,
            **request.data
        },
        "result": {"skill_check": skill_check_result} if skill_check_result else {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Performed action: {request.action_type.value}",
        result={
            "action_type": request.action_type.value,
            "skill_check": skill_check_result
        }
    )


@router.post("/interact", response_model=ActionResponse)
async def interact_with_object(request: InteractRequest) -> ActionResponse:
    """
    Interact with an object or entity at a location.
    Can include skill checks for success.
    """
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Perform skill check if required
    skill_check_result = None
    if request.skill_check:
        roll = random.randint(1, 20)
        total = roll + (request.skill_check.modifier or 0)
        success = total >= request.skill_check.difficulty
        skill_check_result = {
            "roll": roll,
            "total": total,
            "success": success,
            "difficulty": request.skill_check.difficulty
        }
    
    # Create interaction event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "world_interaction",
        "actor": request.actor_id,
        "target": request.target_id,
        "data": {
            "interaction_type": request.interaction_type,
            "target_location": request.target_location.model_dump() if request.target_location else None,
            "skill_check": skill_check_result,
            **request.data
        },
        "result": {"skill_check": skill_check_result} if skill_check_result else {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    message = f"Interacted with {request.target_id or 'object'}: {request.interaction_type}"
    if skill_check_result:
        message += f" (Check: {'Success' if skill_check_result['success'] else 'Failed'})"
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=message,
        result={
            "interaction_type": request.interaction_type,
            "skill_check": skill_check_result
        }
    )


@router.post("/update-location", response_model=ActionResponse)
async def update_location(request: UpdateLocationRequest) -> ActionResponse:
    """
    Directly update a character's location without movement mechanics.
    Useful for GM/admin or instant location changes.
    """
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Create location update event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "location_update",
        "actor": request.character_id,
        "data": {
            "location": request.location.model_dump()
        },
        "result": {}
    }
    
    data_manager.add_event_to_session(request.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Updated location for {request.character_id}",
        result={"location": request.location.model_dump()}
    )


@router.get("/distance", response_model=Dict[str, Any])
async def calculate_distance(
    x1: float, y1: float, z1: float,
    x2: float, y2: float, z2: float,
    include_2d: bool = True
) -> Dict[str, Any]:
    """
    Calculate distance between two coordinates.
    Returns both 3D and 2D distances.
    """
    coord1 = WorldCoordinates(x=x1, y=y1, z=z1)
    coord2 = WorldCoordinates(x=x2, y=y2, z=z2)
    
    distance_3d = coord1.distance_to(coord2)
    distance_2d = coord1.distance_2d(coord2) if include_2d else None
    
    return {
        "from": {"x": x1, "y": y1, "z": z1},
        "to": {"x": x2, "y": y2, "z": z2},
        "distance_3d": round(distance_3d, 2),
        "distance_2d": round(distance_2d, 2) if distance_2d is not None else None
    }


@router.get("/nearby", response_model=Dict[str, Any])
async def get_nearby_entities(
    session_id: str,
    x: float,
    y: float,
    z: float = 0,
    radius: float = 100.0
) -> Dict[str, Any]:
    """
    Get all entities (characters, NPCs) near a coordinate.
    Returns list of entities within radius.
    """
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    center = WorldCoordinates(x=x, y=y, z=z)
    nearby = []
    
    # This is a simplified implementation
    # In a real system, you'd query a spatial database
    
    return {
        "center": {"x": x, "y": y, "z": z},
        "radius": radius,
        "entities": nearby,
        "count": len(nearby)
    }


@router.get("/movement-types", response_model=Dict[str, Any])
async def get_movement_types() -> Dict[str, Any]:
    """
    Get all available movement types with descriptions and speed multipliers.
    """
    return {
        "movement_types": {
            "walk": {
                "speed_multiplier": 1.0,
                "stamina_cost": 0.1,
                "description": "Standard walking pace"
            },
            "run": {
                "speed_multiplier": 2.0,
                "stamina_cost": 0.3,
                "description": "Running speed, moderate stamina cost"
            },
            "sprint": {
                "speed_multiplier": 3.0,
                "stamina_cost": 0.6,
                "description": "Maximum speed, high stamina cost"
            },
            "sneak": {
                "speed_multiplier": 0.5,
                "stamina_cost": 0.15,
                "description": "Slow, stealthy movement"
            },
            "crawl": {
                "speed_multiplier": 0.25,
                "stamina_cost": 0.2,
                "description": "Very slow, low profile"
            },
            "swim": {
                "speed_multiplier": 0.8,
                "stamina_cost": 0.4,
                "description": "Swimming through water"
            },
            "fly": {
                "speed_multiplier": 2.5,
                "stamina_cost": 0.5,
                "description": "Flying through air (requires ability)"
            },
            "climb": {
                "speed_multiplier": 0.6,
                "stamina_cost": 0.5,
                "description": "Climbing vertical surfaces"
            },
            "jump": {
                "speed_multiplier": 1.5,
                "stamina_cost": 0.3,
                "description": "Jumping across gaps"
            },
            "teleport": {
                "speed_multiplier": float('inf'),
                "stamina_cost": 0.0,
                "description": "Instant travel (requires magic)"
            }
        }
    }


@router.get("/action-types", response_model=Dict[str, Any])
async def get_action_types() -> Dict[str, Any]:
    """
    Get all available action types with descriptions.
    """
    return {
        "action_types": {
            "movement": ["move", "teleport"],
            "interaction": ["interact", "use", "examine", "search", "open", "close", "lock", "unlock"],
            "combat": ["attack", "defend", "dodge", "parry"],
            "skills": ["skill_check", "cast_spell", "use_ability"],
            "social": ["talk", "persuade", "intimidate", "deceive"],
            "other": ["rest", "craft", "gather", "custom"]
        }
    }

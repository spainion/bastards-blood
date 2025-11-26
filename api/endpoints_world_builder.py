"""API endpoints for extensive world building with resources, skill areas, and admin tools."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import random

from .auth import verify_api_key, verify_admin
from .models import ActionResponse
from .models_world_builder import (
    WorldRegion, ResourceNode, SkillArea, CraftingStation,
    NPCZone, WorldResource, ResourceType, SkillAreaType,
    CreateRegionRequest, CreateResourceNodeRequest, CreateSkillAreaRequest,
    CreateCraftingStationRequest, CreateNPCZoneRequest,
    GatherResourceRequest, TrainSkillRequest, CraftItemRequest,
    AdminWorldModifyRequest, WorldQueryRequest
)
from .data_manager import data_manager

# Create router for world building endpoints
router = APIRouter(prefix="/api/v1/world-builder", tags=["World Builder"], dependencies=[Depends(verify_api_key)])


@router.post("/admin/region/create", response_model=ActionResponse, dependencies=[Depends(verify_admin)])
async def create_region(request: CreateRegionRequest) -> ActionResponse:
    """
    Admin endpoint: Create a new world region with customizable properties.
    Regions can contain resources, skill areas, crafting stations, and NPC zones.
    """
    region_id = f"region-{data_manager.generate_event_id()}"
    
    region_data = {
        "id": region_id,
        "name": request.name,
        "description": request.description,
        "terrain_type": request.terrain_type,
        "coordinates": {
            "center_x": request.center_x,
            "center_y": request.center_y,
            "center_z": request.center_z,
            "radius": request.radius
        },
        "min_level": request.min_level or 1,
        "max_level": request.max_level or 120,
        "pvp_enabled": request.pvp_enabled,
        "safe_zone": request.safe_zone,
        "resource_nodes": [],
        "skill_areas": [],
        "crafting_stations": [],
        "npc_zones": [],
        "weather": request.weather or "clear",
        "time_of_day": request.time_of_day or "day",
        "custom_properties": request.custom_properties or {},
        "created_at": datetime.now(timezone.utc).isoformat() + 'Z',
        "created_by": request.admin_id
    }
    
    # Save region
    data_manager.save_data(f"world/regions/{region_id}", region_data)
    
    # Log event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "region_created",
        "actor": request.admin_id,
        "data": {
            "region_id": region_id,
            "region_name": request.name,
            "terrain": request.terrain_type
        }
    }
    data_manager.log_event(event)
    
    return ActionResponse(
        success=True,
        message=f"Region '{request.name}' created successfully",
        data={"region_id": region_id, "region": region_data},
        timestamp=datetime.now(timezone.utc).isoformat() + 'Z'
    )


@router.post("/admin/resource/create", response_model=ActionResponse, dependencies=[Depends(verify_admin)])
async def create_resource_node(request: CreateResourceNodeRequest) -> ActionResponse:
    """
    Admin endpoint: Create a resource node (mining, woodcutting, fishing, etc.).
    Players can interact with these to gather resources and gain XP.
    """
    # Verify region exists
    region_data = data_manager.load_data(f"world/regions/{request.region_id}")
    if not region_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region {request.region_id} not found"
        )
    
    node_id = f"resource-{data_manager.generate_event_id()}"
    
    node_data = {
        "id": node_id,
        "name": request.name,
        "resource_type": request.resource_type,
        "skill_required": request.skill_required,
        "level_required": request.level_required or 1,
        "region_id": request.region_id,
        "coordinates": {
            "x": request.x,
            "y": request.y,
            "z": request.z
        },
        "resources": request.resources,  # List of items that can be gathered
        "xp_per_gather": request.xp_per_gather or 10,
        "gather_time": request.gather_time or 3.0,  # seconds
        "respawn_time": request.respawn_time or 30.0,  # seconds
        "max_capacity": request.max_capacity or 100,
        "current_capacity": request.max_capacity or 100,
        "depletion_rate": request.depletion_rate or 1,
        "quality_range": request.quality_range or [1, 100],
        "rare_drop_chance": request.rare_drop_chance or 0.05,
        "description": request.description,
        "created_at": datetime.now(timezone.utc).isoformat() + 'Z',
        "created_by": request.admin_id
    }
    
    # Save node
    data_manager.save_data(f"world/resources/{node_id}", node_data)
    
    # Add to region
    if "resource_nodes" not in region_data:
        region_data["resource_nodes"] = []
    region_data["resource_nodes"].append(node_id)
    data_manager.save_data(f"world/regions/{request.region_id}", region_data)
    
    # Log event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "resource_node_created",
        "actor": request.admin_id,
        "data": {
            "node_id": node_id,
            "resource_type": request.resource_type,
            "region_id": request.region_id
        }
    }
    data_manager.log_event(event)
    
    return ActionResponse(
        success=True,
        message=f"Resource node '{request.name}' created successfully",
        data={"node_id": node_id, "node": node_data},
        timestamp=datetime.now(timezone.utc).isoformat() + 'Z'
    )


@router.post("/admin/skill-area/create", response_model=ActionResponse, dependencies=[Depends(verify_admin)])
async def create_skill_area(request: CreateSkillAreaRequest) -> ActionResponse:
    """
    Admin endpoint: Create a skill training area.
    Provides bonuses or special training opportunities for specific skills.
    """
    # Verify region exists
    region_data = data_manager.load_data(f"world/regions/{request.region_id}")
    if not region_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region {request.region_id} not found"
        )
    
    area_id = f"skill-area-{data_manager.generate_event_id()}"
    
    area_data = {
        "id": area_id,
        "name": request.name,
        "area_type": request.area_type,
        "skills_trained": request.skills_trained,
        "region_id": request.region_id,
        "coordinates": {
            "x": request.x,
            "y": request.y,
            "z": request.z,
            "radius": request.radius or 50.0
        },
        "xp_bonus": request.xp_bonus or 1.0,  # Multiplier (1.5 = 50% bonus)
        "level_requirements": request.level_requirements or {},
        "access_cost": request.access_cost or 0,
        "activities": request.activities or [],
        "npcs": request.npcs or [],
        "description": request.description,
        "created_at": datetime.now(timezone.utc).isoformat() + 'Z',
        "created_by": request.admin_id
    }
    
    # Save area
    data_manager.save_data(f"world/skill-areas/{area_id}", area_data)
    
    # Add to region
    if "skill_areas" not in region_data:
        region_data["skill_areas"] = []
    region_data["skill_areas"].append(area_id)
    data_manager.save_data(f"world/regions/{request.region_id}", region_data)
    
    # Log event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "skill_area_created",
        "actor": request.admin_id,
        "data": {
            "area_id": area_id,
            "area_type": request.area_type,
            "skills": request.skills_trained,
            "region_id": request.region_id
        }
    }
    data_manager.log_event(event)
    
    return ActionResponse(
        success=True,
        message=f"Skill area '{request.name}' created successfully",
        data={"area_id": area_id, "area": area_data},
        timestamp=datetime.now(timezone.utc).isoformat() + 'Z'
    )


@router.post("/admin/crafting-station/create", response_model=ActionResponse, dependencies=[Depends(verify_admin)])
async def create_crafting_station(request: CreateCraftingStationRequest) -> ActionResponse:
    """
    Admin endpoint: Create a crafting station (forge, workbench, alchemy lab, etc.).
    Players can use these to craft items with bonuses or special recipes.
    """
    # Verify region exists
    region_data = data_manager.load_data(f"world/regions/{request.region_id}")
    if not region_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region {request.region_id} not found"
        )
    
    station_id = f"crafting-station-{data_manager.generate_event_id()}"
    
    station_data = {
        "id": station_id,
        "name": request.name,
        "station_type": request.station_type,
        "region_id": request.region_id,
        "coordinates": {
            "x": request.x,
            "y": request.y,
            "z": request.z
        },
        "crafting_skills": request.crafting_skills,  # Which skills can use this station
        "level_bonus": request.level_bonus or 0,  # Bonus to crafting success
        "speed_bonus": request.speed_bonus or 1.0,  # Crafting speed multiplier
        "quality_bonus": request.quality_bonus or 0,  # Bonus to item quality
        "special_recipes": request.special_recipes or [],  # Exclusive recipes
        "requirements": request.requirements or {},
        "usage_cost": request.usage_cost or 0,
        "max_tier": request.max_tier or 5,
        "description": request.description,
        "created_at": datetime.now(timezone.utc).isoformat() + 'Z',
        "created_by": request.admin_id
    }
    
    # Save station
    data_manager.save_data(f"world/crafting-stations/{station_id}", station_data)
    
    # Add to region
    if "crafting_stations" not in region_data:
        region_data["crafting_stations"] = []
    region_data["crafting_stations"].append(station_id)
    data_manager.save_data(f"world/regions/{request.region_id}", region_data)
    
    # Log event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "crafting_station_created",
        "actor": request.admin_id,
        "data": {
            "station_id": station_id,
            "station_type": request.station_type,
            "region_id": request.region_id
        }
    }
    data_manager.log_event(event)
    
    return ActionResponse(
        success=True,
        message=f"Crafting station '{request.name}' created successfully",
        data={"station_id": station_id, "station": station_data},
        timestamp=datetime.now(timezone.utc).isoformat() + 'Z'
    )


@router.post("/admin/npc-zone/create", response_model=ActionResponse, dependencies=[Depends(verify_admin)])
async def create_npc_zone(request: CreateNPCZoneRequest) -> ActionResponse:
    """
    Admin endpoint: Create an NPC combat zone with enemies that players can fight.
    NPCs spawn automatically and provide XP/loot when defeated.
    """
    # Verify region exists
    region_data = data_manager.load_data(f"world/regions/{request.region_id}")
    if not region_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region {request.region_id} not found"
        )
    
    zone_id = f"npc-zone-{data_manager.generate_event_id()}"
    
    zone_data = {
        "id": zone_id,
        "name": request.name,
        "region_id": request.region_id,
        "coordinates": {
            "center_x": request.center_x,
            "center_y": request.center_y,
            "center_z": request.center_z,
            "radius": request.radius or 100.0
        },
        "npc_types": request.npc_types,  # List of NPC/enemy templates to spawn
        "spawn_rate": request.spawn_rate or 30.0,  # seconds between spawns
        "max_npcs": request.max_npcs or 10,
        "min_level": request.min_level or 1,
        "max_level": request.max_level or 10,
        "aggressive": request.aggressive,
        "combat_xp_bonus": request.combat_xp_bonus or 1.0,
        "loot_bonus": request.loot_bonus or 1.0,
        "boss_spawn_chance": request.boss_spawn_chance or 0.05,
        "boss_templates": request.boss_templates or [],
        "active": True,
        "description": request.description,
        "created_at": datetime.now(timezone.utc).isoformat() + 'Z',
        "created_by": request.admin_id,
        "current_npcs": []
    }
    
    # Save zone
    data_manager.save_data(f"world/npc-zones/{zone_id}", zone_data)
    
    # Add to region
    if "npc_zones" not in region_data:
        region_data["npc_zones"] = []
    region_data["npc_zones"].append(zone_id)
    data_manager.save_data(f"world/regions/{request.region_id}", region_data)
    
    # Log event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "npc_zone_created",
        "actor": request.admin_id,
        "data": {
            "zone_id": zone_id,
            "npc_types": request.npc_types,
            "region_id": request.region_id
        }
    }
    data_manager.log_event(event)
    
    return ActionResponse(
        success=True,
        message=f"NPC zone '{request.name}' created successfully",
        data={"zone_id": zone_id, "zone": zone_data},
        timestamp=datetime.now(timezone.utc).isoformat() + 'Z'
    )


@router.post("/gather", response_model=ActionResponse)
async def gather_resource(request: GatherResourceRequest) -> ActionResponse:
    """
    Player action: Gather resources from a resource node.
    Requires appropriate skill level and provides XP.
    """
    # Verify session
    session_data = data_manager.load_session(request.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found"
        )
    
    # Load resource node
    node_data = data_manager.load_data(f"world/resources/{request.node_id}")
    if not node_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource node {request.node_id} not found"
        )
    
    # Load character
    char_data = data_manager.load_character(request.character_id)
    if not char_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {request.character_id} not found"
        )
    
    # Check skill level
    skills = char_data.get("skills", {})
    required_skill = node_data["skill_required"]
    required_level = node_data["level_required"]
    
    player_skill_level = skills.get(required_skill, {}).get("level", 1)
    if player_skill_level < required_level:
        return ActionResponse(
            success=False,
            message=f"Insufficient {required_skill} level (required: {required_level}, current: {player_skill_level})",
            timestamp=datetime.now(timezone.utc).isoformat() + 'Z'
        )
    
    # Check if node is depleted
    if node_data["current_capacity"] <= 0:
        return ActionResponse(
            success=False,
            message=f"Resource node '{node_data['name']}' is depleted. Wait for respawn.",
            timestamp=datetime.now(timezone.utc).isoformat() + 'Z'
        )
    
    # Determine what was gathered
    resources = node_data["resources"]
    gathered_resource = random.choice(resources)
    
    # Calculate quality based on player level vs requirement
    quality_min, quality_max = node_data["quality_range"]
    level_bonus = min((player_skill_level - required_level) * 2, 20)
    quality = random.randint(quality_min, quality_max) + level_bonus
    quality = min(quality, 100)
    
    # Check for rare drop
    rare_drop = None
    if random.random() < node_data["rare_drop_chance"]:
        rare_drop = f"rare_{gathered_resource}"
    
    # Grant XP
    xp_gained = node_data["xp_per_gather"]
    
    # Update node capacity
    node_data["current_capacity"] -= node_data["depletion_rate"]
    data_manager.save_data(f"world/resources/{request.node_id}", node_data)
    
    # Add resource to character inventory
    if "inventory" not in char_data:
        char_data["inventory"] = {}
    if gathered_resource not in char_data["inventory"]:
        char_data["inventory"][gathered_resource] = 0
    char_data["inventory"][gathered_resource] += 1
    
    if rare_drop:
        if rare_drop not in char_data["inventory"]:
            char_data["inventory"][rare_drop] = 0
        char_data["inventory"][rare_drop] += 1
    
    # Update skill XP
    if required_skill not in skills:
        skills[required_skill] = {"level": 1, "xp": 0}
    skills[required_skill]["xp"] += xp_gained
    char_data["skills"] = skills
    
    data_manager.save_character(request.character_id, char_data)
    
    # Log event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "resource_gathered",
        "actor": request.character_id,
        "data": {
            "node_id": request.node_id,
            "resource": gathered_resource,
            "quality": quality,
            "rare_drop": rare_drop,
            "xp_gained": xp_gained,
            "skill": required_skill
        }
    }
    data_manager.log_event(event)
    
    result_message = f"Gathered {gathered_resource} (quality: {quality})"
    if rare_drop:
        result_message += f" and found rare {rare_drop}!"
    result_message += f" (+{xp_gained} {required_skill} XP)"
    
    return ActionResponse(
        success=True,
        message=result_message,
        data={
            "resource": gathered_resource,
            "quality": quality,
            "rare_drop": rare_drop,
            "xp_gained": xp_gained,
            "skill": required_skill,
            "new_skill_xp": skills[required_skill]["xp"]
        },
        timestamp=datetime.now(timezone.utc).isoformat() + 'Z'
    )


@router.get("/regions", response_model=ActionResponse)
async def list_regions() -> ActionResponse:
    """
    List all world regions with their properties.
    """
    # Load all regions
    regions = []
    region_files = data_manager.list_files("world/regions/")
    
    for region_file in region_files:
        region_data = data_manager.load_data(f"world/regions/{region_file}")
        if region_data:
            regions.append({
                "id": region_data["id"],
                "name": region_data["name"],
                "description": region_data.get("description", ""),
                "terrain": region_data.get("terrain_type", "plains"),
                "min_level": region_data.get("min_level", 1),
                "max_level": region_data.get("max_level", 120),
                "pvp_enabled": region_data.get("pvp_enabled", False),
                "safe_zone": region_data.get("safe_zone", False),
                "resource_count": len(region_data.get("resource_nodes", [])),
                "skill_area_count": len(region_data.get("skill_areas", [])),
                "crafting_station_count": len(region_data.get("crafting_stations", [])),
                "npc_zone_count": len(region_data.get("npc_zones", []))
            })
    
    return ActionResponse(
        success=True,
        message=f"Found {len(regions)} regions",
        data={"regions": regions},
        timestamp=datetime.now(timezone.utc).isoformat() + 'Z'
    )


@router.get("/region/{region_id}", response_model=ActionResponse)
async def get_region_details(region_id: str) -> ActionResponse:
    """
    Get detailed information about a specific region including all its features.
    """
    region_data = data_manager.load_data(f"world/regions/{region_id}")
    if not region_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Region {region_id} not found"
        )
    
    # Load details of all features
    resource_nodes = []
    for node_id in region_data.get("resource_nodes", []):
        node = data_manager.load_data(f"world/resources/{node_id}")
        if node:
            resource_nodes.append(node)
    
    skill_areas = []
    for area_id in region_data.get("skill_areas", []):
        area = data_manager.load_data(f"world/skill-areas/{area_id}")
        if area:
            skill_areas.append(area)
    
    crafting_stations = []
    for station_id in region_data.get("crafting_stations", []):
        station = data_manager.load_data(f"world/crafting-stations/{station_id}")
        if station:
            crafting_stations.append(station)
    
    npc_zones = []
    for zone_id in region_data.get("npc_zones", []):
        zone = data_manager.load_data(f"world/npc-zones/{zone_id}")
        if zone:
            npc_zones.append(zone)
    
    return ActionResponse(
        success=True,
        message=f"Region details for '{region_data['name']}'",
        data={
            "region": region_data,
            "resource_nodes": resource_nodes,
            "skill_areas": skill_areas,
            "crafting_stations": crafting_stations,
            "npc_zones": npc_zones
        },
        timestamp=datetime.now(timezone.utc).isoformat() + 'Z'
    )


@router.get("/resources/nearby", response_model=ActionResponse)
async def find_nearby_resources(
    character_id: str,
    session_id: str,
    radius: float = 100.0
) -> ActionResponse:
    """
    Find resource nodes near a character's current location.
    """
    # Verify session
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    # Load character
    char_data = data_manager.load_character(character_id)
    if not char_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found"
        )
    
    # Get character location
    char_loc = char_data.get("location", {}).get("position", {})
    char_x = char_loc.get("x", 0)
    char_y = char_loc.get("y", 0)
    
    # Find nearby resources
    nearby_resources = []
    resource_files = data_manager.list_files("world/resources/")
    
    for resource_file in resource_files:
        resource = data_manager.load_data(f"world/resources/{resource_file}")
        if resource:
            res_x = resource["coordinates"]["x"]
            res_y = resource["coordinates"]["y"]
            distance = ((res_x - char_x) ** 2 + (res_y - char_y) ** 2) ** 0.5
            
            if distance <= radius:
                nearby_resources.append({
                    "id": resource["id"],
                    "name": resource["name"],
                    "type": resource["resource_type"],
                    "skill_required": resource["skill_required"],
                    "level_required": resource["level_required"],
                    "distance": round(distance, 2),
                    "available": resource["current_capacity"] > 0,
                    "capacity": f"{resource['current_capacity']}/{resource['max_capacity']}"
                })
    
    # Sort by distance
    nearby_resources.sort(key=lambda x: x["distance"])
    
    return ActionResponse(
        success=True,
        message=f"Found {len(nearby_resources)} resources within {radius} units",
        data={"resources": nearby_resources},
        timestamp=datetime.now(timezone.utc).isoformat() + 'Z'
    )

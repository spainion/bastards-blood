"""Combat system and enemy management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import random
import math

from .database import get_db, DBEnemy, DBCharacter, CombatLog, User
from .models_combat import (
    Enemy, CombatAction, CombatResult, SpawnEnemyRequest,
    EnemyListQuery, EnemyType, DamageType, AIBehavior, CombatStats
)
from .endpoints_users import verify_token
from .data_manager import RPGDataManager

router = APIRouter(prefix="/api/v1/combat", tags=["Combat & Enemies"])

# Enemy templates
ENEMY_TEMPLATES = {
    "goblin": {"name": "Goblin", "type": EnemyType.GOBLIN, "level": 5, "hp_base": 30, "damage_base": 5, "xp": 25},
    "orc": {"name": "Orc", "type": EnemyType.ORC, "level": 15, "hp_base": 100, "damage_base": 15, "xp": 75},
    "troll": {"name": "Troll", "type": EnemyType.TROLL, "level": 25, "hp_base": 250, "damage_base": 30, "xp": 200},
    "dragon": {"name": "Dragon", "type": EnemyType.DRAGON, "level": 50, "hp_base": 1000, "damage_base": 100, "xp": 1000},
    "skeleton": {"name": "Skeleton", "type": EnemyType.UNDEAD, "level": 10, "hp_base": 50, "damage_base": 10, "xp": 50},
    "zombie": {"name": "Zombie", "type": EnemyType.UNDEAD, "level": 12, "hp_base": 80, "damage_base": 12, "xp": 60},
    "demon": {"name": "Demon", "type": EnemyType.DEMON, "level": 40, "hp_base": 600, "damage_base": 75, "xp": 750},
    "wolf": {"name": "Wolf", "type": EnemyType.BEAST, "level": 8, "hp_base": 40, "damage_base": 8, "xp": 35},
    "bear": {"name": "Bear", "type": EnemyType.BEAST, "level": 20, "hp_base": 200, "damage_base": 25, "xp": 150},
    "boss_demon_lord": {"name": "Demon Lord", "type": EnemyType.BOSS, "level": 75, "hp_base": 5000, "damage_base": 200, "xp": 5000},
}


def calculate_combat_damage(
    attacker_level: int,
    attacker_stats: Dict[str, int],
    damage_min: int,
    damage_max: int,
    defender_armor: int,
    skill_bonus: int = 0
) -> Dict[str, Any]:
    """Calculate combat damage with rolls."""
    # Base damage roll
    base_damage = random.randint(damage_min, damage_max)
    
    # Strength modifier
    str_bonus = attacker_stats.get("STR", 10) - 10
    
    # Critical hit check (5% chance)
    critical = random.random() < 0.05
    if critical:
        base_damage *= 2
    
    # Miss check (5% chance)
    miss = random.random() < 0.05
    if miss:
        return {
            "damage": 0,
            "was_critical": False,
            "was_miss": True,
            "armor_mitigation": 0
        }
    
    # Apply modifiers
    total_damage = base_damage + str_bonus + skill_bonus
    
    # Armor mitigation (reduces damage by armor%)
    armor_reduction = min(defender_armor * 0.5, total_damage * 0.75)  # Max 75% reduction
    final_damage = max(1, int(total_damage - armor_reduction))  # Min 1 damage
    
    return {
        "damage": final_damage,
        "was_critical": critical,
        "was_miss": False,
        "armor_mitigation": int(armor_reduction)
    }


@router.post("/spawn-enemy", response_model=List[str])
def spawn_enemy(
    request: SpawnEnemyRequest,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Spawn enemy/mob in the game world.
    
    Spawns one or more enemies based on template at specified location.
    """
    template_name = request.enemy_template.lower()
    if template_name not in ENEMY_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Unknown enemy template: {request.enemy_template}")
    
    template = ENEMY_TEMPLATES[template_name]
    spawned_ids = []
    
    for i in range(request.quantity):
        # Generate enemy ID
        enemy_id = f"enemy-{template_name}-{datetime.now(timezone.utc).timestamp()}-{i}"
        
        # Determine level
        level = request.level_override or template["level"]
        
        # Scale HP and damage with level
        hp_max = int(template["hp_base"] * (1 + (level - template["level"]) * 0.1))
        damage_min = max(1, int(template["damage_base"] * 0.8 * (1 + (level - template["level"]) * 0.1)))
        damage_max = int(template["damage_base"] * 1.2 * (1 + (level - template["level"]) * 0.1))
        xp_reward = int(template["xp"] * (1 + (level - template["level"]) * 0.15))
        
        # Calculate stats based on level
        stats = {
            "STR": 10 + level // 2,
            "DEX": 10 + level // 3,
            "CON": 10 + level // 2,
            "INT": 5 + level // 5,
            "WIS": 5 + level // 5,
            "CHA": 5
        }
        
        # Create enemy in database
        enemy = DBEnemy(
            id=enemy_id,
            name=f"{template['name']} (Lvl {level})",
            enemy_type=template["type"].value,
            level=level,
            stats=stats,
            hp_max=hp_max,
            hp_current=hp_max,
            damage_min=damage_min,
            damage_max=damage_max,
            armor=level * 2,
            xp_reward=xp_reward,
            spawn_x=request.location["x"],
            spawn_y=request.location["y"],
            spawn_z=request.location.get("z", 0.0),
            current_x=request.location["x"],
            current_y=request.location["y"],
            current_z=request.location.get("z", 0.0),
            region=request.region
        )
        
        db.add(enemy)
        spawned_ids.append(enemy_id)
    
    db.commit()
    
    return spawned_ids


@router.get("/enemies", response_model=List[Dict[str, Any]])
def list_enemies(
    session_id: str,
    region: str = None,
    enemy_type: str = None,
    alive_only: bool = True,
    within_range: float = None,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    List enemies in the game world.
    
    Returns list of enemies with optional filtering.
    """
    query = db.query(DBEnemy)
    
    if alive_only:
        query = query.filter(DBEnemy.is_alive == True)
    
    if region:
        query = query.filter(DBEnemy.region == region)
    
    if enemy_type:
        query = query.filter(DBEnemy.enemy_type == enemy_type)
    
    enemies = query.all()
    
    # Convert to dict
    result = []
    for enemy in enemies:
        result.append({
            "id": enemy.id,
            "name": enemy.name,
            "type": enemy.enemy_type,
            "level": enemy.level,
            "hp": {"max": enemy.hp_max, "current": enemy.hp_current},
            "location": {"x": enemy.current_x, "y": enemy.current_y, "z": enemy.current_z},
            "region": enemy.region,
            "is_alive": enemy.is_alive
        })
    
    return result


@router.post("/attack", response_model=CombatResult)
def perform_combat_action(
    action: CombatAction,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Perform a combat action (attack, spell, ability).
    
    Executes combat action and returns detailed results with damage, HP changes, and rewards.
    """
    # Get attacker (character or enemy)
    attacker = db.query(DBCharacter).filter(DBCharacter.id == action.attacker_id).first()
    is_player_attacker = attacker is not None
    
    if not attacker:
        attacker = db.query(DBEnemy).filter(DBEnemy.id == action.attacker_id).first()
    
    if not attacker:
        raise HTTPException(status_code=404, detail="Attacker not found")
    
    # Get defender (character or enemy)
    defender = db.query(DBCharacter).filter(DBCharacter.id == action.defender_id).first()
    is_player_defender = defender is not None
    
    if not defender:
        defender = db.query(DBEnemy).filter(DBEnemy.id == action.defender_id).first()
    
    if not defender:
        raise HTTPException(status_code=404, detail="Defender not found")
    
    # Check if alive
    if hasattr(attacker, 'hp_current'):
        if attacker.hp_current <= 0:
            raise HTTPException(status_code=400, detail="Attacker is dead")
    if hasattr(defender, 'hp_current'):
        if defender.hp_current <= 0:
            raise HTTPException(status_code=400, detail="Defender is already dead")
    
    # Store state before attack
    attacker_hp_before = attacker.hp_current if hasattr(attacker, 'hp_current') else 0
    defender_hp_before = defender.hp_current if hasattr(defender, 'hp_current') else 0
    
    # Calculate damage
    if is_player_attacker:
        damage_result = calculate_combat_damage(
            attacker.level,
            attacker.stats,
            action.data.get("damage_min", 5),
            action.data.get("damage_max", 15),
            getattr(defender, "armor", 0),
            action.data.get("skill_bonus", 0)
        )
    else:
        damage_result = calculate_combat_damage(
            attacker.level,
            attacker.stats,
            attacker.damage_min,
            attacker.damage_max,
            action.data.get("defender_armor", 0),
            0
        )
    
    # Apply damage
    damage = damage_result["damage"]
    defender.hp_current = max(0, defender.hp_current - damage)
    
    # Check if defender defeated
    defender_defeated = defender.hp_current == 0
    if defender_defeated:
        if hasattr(defender, 'is_alive'):
            defender.is_alive = False
            if isinstance(defender, DBEnemy):
                defender.last_death = datetime.now(timezone.utc)
    
    # Calculate rewards (if player killed enemy)
    xp_gained = 0
    loot_dropped = []
    if defender_defeated and is_player_attacker and isinstance(defender, DBEnemy):
        xp_gained = defender.xp_reward
        # Simple loot (could be enhanced with loot tables)
        if random.random() < 0.5:  # 50% chance for gold
            loot_dropped.append({
                "type": "currency",
                "currency_type": "gold",
                "amount": random.randint(defender.level * 5, defender.level * 20)
            })
    
    # Log combat
    combat_log = CombatLog(
        session_id=action.session_id,
        combat_id=f"combat-{datetime.now(timezone.utc).timestamp()}",
        attacker_id=action.attacker_id,
        attacker_type="player" if is_player_attacker else "enemy",
        defender_id=action.defender_id,
        defender_type="player" if is_player_defender else "enemy",
        action_type=action.action_type,
        damage_dealt=damage,
        was_critical=damage_result["was_critical"],
        was_miss=damage_result["was_miss"],
        attacker_hp_before=attacker_hp_before,
        attacker_hp_after=getattr(attacker, 'hp_current', 0),
        defender_hp_before=defender_hp_before,
        defender_hp_after=defender.hp_current,
        defender_defeated=defender_defeated,
        xp_gained=xp_gained,
        loot_dropped=loot_dropped
    )
    db.add(combat_log)
    db.commit()
    
    # Build result message
    if damage_result["was_miss"]:
        message = f"{action.attacker_id} missed {action.defender_id}!"
    elif damage_result["was_critical"]:
        message = f"CRITICAL HIT! {action.attacker_id} dealt {damage} damage to {action.defender_id}!"
    else:
        message = f"{action.attacker_id} dealt {damage} damage to {action.defender_id}"
    
    if defender_defeated:
        message += f" {action.defender_id} has been defeated!"
    
    details = [
        f"Damage roll: {damage}",
        f"Armor mitigation: {damage_result.get('armor_mitigation', 0)}",
        f"Defender HP: {defender_hp_before} -> {defender.hp_current}"
    ]
    
    if xp_gained > 0:
        details.append(f"XP gained: {xp_gained}")
    
    return CombatResult(
        success=not damage_result["was_miss"],
        damage_dealt=damage,
        damage_type=DamageType.PHYSICAL,
        was_critical=damage_result["was_critical"],
        was_miss=damage_result["was_miss"],
        attacker_hp={"max": getattr(attacker, 'hp_max', 0), "current": getattr(attacker, 'hp_current', 0)},
        defender_hp={"max": defender.hp_max, "current": defender.hp_current},
        defender_defeated=defender_defeated,
        xp_gained=xp_gained,
        loot_dropped=loot_dropped,
        message=message,
        details=details
    )


@router.get("/combat-log/{session_id}", response_model=List[Dict[str, Any]])
def get_combat_log(
    session_id: str,
    limit: int = 50,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Get combat log for a session.
    
    Returns recent combat actions and results.
    """
    logs = db.query(CombatLog).filter(
        CombatLog.session_id == session_id
    ).order_by(CombatLog.timestamp.desc()).limit(limit).all()
    
    result = []
    for log in logs:
        result.append({
            "combat_id": log.combat_id,
            "attacker": log.attacker_id,
            "attacker_type": log.attacker_type,
            "defender": log.defender_id,
            "defender_type": log.defender_type,
            "action": log.action_type,
            "damage": log.damage_dealt,
            "critical": log.was_critical,
            "miss": log.was_miss,
            "defeated": log.defender_defeated,
            "xp_gained": log.xp_gained,
            "timestamp": log.timestamp.isoformat()
        })
    
    return result


@router.get("/enemy-templates", response_model=Dict[str, Any])
def get_enemy_templates():
    """
    Get available enemy templates.
    
    Returns list of enemy templates that can be spawned.
    """
    return ENEMY_TEMPLATES

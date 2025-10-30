# RuneScape-Style Progressive Skills System Guide

This guide covers the comprehensive RuneScape-style skills system in Bastards Blood RPG, featuring progressive leveling from 1 to 120, tier-based equipment and resources, and gameplay-affecting mechanics.

## Table of Contents

- [Overview](#overview)
- [Skills List](#skills-list)
- [Leveling System](#leveling-system)
- [Tier System](#tier-system)
- [Skill Mechanics](#skill-mechanics)
- [API Endpoints](#api-endpoints)
- [Examples](#examples)

## Overview

The progressive skills system provides:

- **120 Level Cap**: Skills can be trained from level 1 to 120
- **24 Skills**: Combat, gathering, artisan, crafting, magic, and support skills
- **Exponential XP**: RuneScape-based XP formula for realistic progression
- **Tier System**: 7 tiers from Bronze to Dragon unlocked by level
- **Progressive Checks**: Higher levels directly increase success rates
- **Content Unlocking**: New items, resources, and areas unlock at specific levels
- **Total and Combat Levels**: Overall progression tracking

## Skills List

### Combat Skills (7)
- **Attack** - Accuracy with melee weapons
- **Strength** - Damage with melee weapons
- **Defence** - Armor effectiveness and damage reduction
- **Ranged** - Accuracy and damage with ranged weapons
- **Magic** - Spell effectiveness and magical power
- **Hitpoints** - Health pool and regeneration (starts at level 10)
- **Prayer** - Divine power and buff duration

### Gathering Skills (5)
- **Mining** - Extracting ores from rocks
- **Fishing** - Catching fish and sea creatures
- **Woodcutting** - Chopping logs from trees
- **Hunter** - Trapping and tracking creatures
- **Farming** - Growing crops and herbs

### Artisan Skills (6)
- **Smithing** - Creating metal equipment
- **Cooking** - Preparing food
- **Firemaking** - Starting and maintaining fires
- **Construction** - Building structures and furniture

### Crafting Skills (3)
- **Crafting** - Making armor, jewelry, and items
- **Fletching** - Creating bows and arrows
- **Herblore** - Brewing potions and elixirs

### Magic Skills (2)
- **Runecrafting** - Creating magical runes
- **Summoning** - Calling forth familiars

### Support Skills (3)
- **Agility** - Movement speed and stamina efficiency
- **Thieving** - Pickpocketing and lockpicking
- **Dungeoneering** - Exploring dungeons
- **Slayer** - Hunting specific creatures

## Leveling System

### XP Formula

The system uses the RuneScape XP formula:

```
XP for level L = sum from 1 to (L-1) of floor(level + 300 * 2^(level/7)) / 4
```

### XP Requirements (Examples)

| Level | Total XP | XP to Next |
|-------|----------|------------|
| 1 | 0 | 83 |
| 10 | 1,154 | 276 |
| 20 | 4,470 | 598 |
| 30 | 13,363 | 1,096 |
| 40 | 37,224 | 1,962 |
| 50 | 101,333 | 3,258 |
| 60 | 273,742 | 5,346 |
| 70 | 737,627 | 8,740 |
| 80 | 1,986,068 | 14,391 |
| 90 | 5,346,332 | 23,905 |
| 99 | 13,034,431 | - |
| 120 | 104,273,167 | - |

### Automatic Level-Ups

When you gain XP:
1. XP is added to skill total
2. System checks if you've reached next level threshold
3. Level automatically increases
4. Multiple level-ups can occur from single XP gain
5. Events are generated for each level-up

## Tier System

### Tier Levels

| Tier | Level Required | Multiplier | Color |
|------|----------------|------------|-------|
| Bronze | 1 | 1.0x | #CD7F32 |
| Iron | 15 | 1.2x | #C0C0C0 |
| Steel | 30 | 1.4x | #808080 |
| Mithril | 50 | 1.6x | #0000FF |
| Adamant | 70 | 1.8x | #00FF00 |
| Rune | 90 | 2.0x | #00FFFF |
| Dragon | 99 | 2.5x | #FF0000 |

### Tier Benefits

- **Equipment**: Higher tier weapons and armor
- **Resources**: Access to better quality materials
- **Effectiveness**: Tier multiplier applied to actions
- **Success Rates**: Better tiers improve outcomes

### Getting Current Tier

```python
# Character at level 55 Mining
tier = skill.tier  # Returns "mithril"
```

## Skill Mechanics

### Skill Bonuses

Each 10 levels provides +1 bonus modifier:
- Level 1-9: +0
- Level 10-19: +1
- Level 20-29: +2
- ...
- Level 110-120: +12

### Success Multiplier

Success rate increases linearly with level:
```
Multiplier = 1.0 + (level - 1) / 99.0
```

Examples:
- Level 1: 1.00x (100%)
- Level 50: 1.495x (149.5%)
- Level 99: 2.00x (200%)

### Progressive Skill Checks

Success rate based on level vs difficulty:
```
Base Rate = 50% + (Character Level - Difficulty) * 5%
Clamped between 5% and 95%
```

Examples:
- Level 50 vs DC 50: 50% success
- Level 60 vs DC 50: 100% → capped at 95%
- Level 40 vs DC 50: 0% → minimum 5%

Critical successes (5%) and failures (5%) can occur.

## API Endpoints

All endpoints require authentication via `X-API-Key` header.

### GET /api/v1/skills/overview
Get complete overview of character's skills.

**Query Parameters:**
- `character_id` (string, required): Character ID

**Response:**
```json
{
  "character_id": "char-hero",
  "skills": [
    {
      "name": "Mining",
      "level": 55,
      "xp": 166636,
      "xp_to_next": 3654,
      "progress": 0.42,
      "category": "gathering",
      "tier": "mithril",
      "bonus": 5
    }
  ],
  "total_level": 1234,
  "combat_level": 87,
  "unlocks": []
}
```

### GET /api/v1/skills/skill/{skill_name}
Get detailed information about a specific skill.

**Query Parameters:**
- `character_id` (string, required): Character ID
- `skill_name` (string, path): Skill name

**Response:**
```json
{
  "name": "Mining",
  "level": 55,
  "xp": 166636,
  "xp_to_next": 3654,
  "progress_percent": 42.3,
  "category": "gathering",
  "current_tier": "mithril",
  "accessible_tiers": [
    {"name": "bronze", "level_required": 1},
    {"name": "iron", "level_required": 15},
    {"name": "steel", "level_required": 30},
    {"name": "mithril", "level_required": 50}
  ],
  "next_tier": {
    "name": "adamant",
    "level_required": 70
  },
  "bonus": 5,
  "success_multiplier": 1.545
}
```

### POST /api/v1/skills/add-xp
Add XP to a skill with automatic leveling.

**Request Body:**
```json
{
  "session_id": "game-001",
  "character_id": "char-hero",
  "skill_name": "Mining",
  "xp_amount": 1000,
  "reason": "Mined 10 iron ore"
}
```

**Response:**
```json
{
  "success": true,
  "xp_gained": 1000,
  "level_ups": [
    {
      "skill": "Mining",
      "new_level": 56,
      "tier": "mithril",
      "bonus": 5
    }
  ],
  "items_produced": [],
  "new_level": 56,
  "new_xp": 167636,
  "message": "Gained 1000 XP in Mining. Level up! Level 56"
}
```

### POST /api/v1/skills/progressive-check
Perform a progressive skill check.

**Request Body:**
```json
{
  "session_id": "game-001",
  "character_id": "char-hero",
  "skill_name": "Mining",
  "difficulty": 50,
  "use_random": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Mining check (Lvl 55 vs DC 50): Success",
  "data": {
    "check": {
      "skill_name": "Mining",
      "difficulty": 50,
      "character_level": 55,
      "roll": 68,
      "success": true,
      "margin": 7,
      "critical_success": false,
      "critical_failure": false
    },
    "success_rate_percent": 75.0,
    "tier": "mithril",
    "bonus": 5
  }
}
```

### POST /api/v1/skills/perform-action
Perform an action that trains a skill.

**Request Body:**
```json
{
  "session_id": "game-001",
  "character_id": "char-hero",
  "skill_name": "Mining",
  "action_name": "mine_iron",
  "quantity": 5
}
```

**Response:**
```json
{
  "success": true,
  "xp_gained": 175,
  "level_ups": [],
  "items_produced": [
    {"name": "Mine Iron", "quantity": 1},
    {"name": "Mine Iron", "quantity": 1},
    {"name": "Mine Iron", "quantity": 1},
    {"name": "Mine Iron", "quantity": 1},
    {"name": "Mine Iron", "quantity": 1}
  ],
  "new_level": 55,
  "new_xp": 166811,
  "message": "Performed mine_iron 5/5 times. Gained 175 XP."
}
```

### POST /api/v1/skills/check-requirements
Check if character meets skill requirements.

**Request Body:**
```json
{
  "character_id": "char-hero",
  "requirements": [
    {
      "skill_name": "Mining",
      "level_required": 50,
      "optional": false
    },
    {
      "skill_name": "Smithing",
      "level_required": 60,
      "optional": false
    }
  ]
}
```

**Response:**
```json
{
  "success": false,
  "message": "Some requirements not met",
  "data": {
    "requirements": [
      {
        "skill": "Mining",
        "required": 50,
        "current": 55,
        "met": true,
        "optional": false
      },
      {
        "skill": "Smithing",
        "required": 60,
        "current": 45,
        "met": false,
        "optional": false
      }
    ]
  }
}
```

### GET /api/v1/skills/tiers
Get list of all tiers.

**Response:**
```json
[
  {
    "name": "bronze",
    "level_required": 1,
    "color": "#CD7F32",
    "multiplier": 1.0,
    "description": null
  },
  ...
]
```

### GET /api/v1/skills/available-skills
Get list of all available skills.

**Response:**
```json
[
  {"name": "Attack", "category": "combat"},
  {"name": "Mining", "category": "gathering"},
  {"name": "Smithing", "category": "artisan"},
  ...
]
```

## Examples

### Example 1: Training Mining Skill

```python
import requests

BASE_URL = "http://localhost:8000"
HEADERS = {"X-API-Key": "your-secret-key"}

# Start a session
requests.post(
    f"{BASE_URL}/api/v1/sessions",
    headers=HEADERS,
    params={"session_id": "training-001", "campaign": "skill_training"}
)

# Create character (skills auto-initialize)
character = {
    "id": "char-miner",
    "name": "Rocky the Miner",
    "class": "Prospector",
    "stats": {"STR": 14, "DEX": 10, "CON": 16},
    "hp": {"max": 50, "current": 50}
}
requests.post(f"{BASE_URL}/api/v1/characters", headers=HEADERS, json=character)

# Check current mining level
response = requests.get(
    f"{BASE_URL}/api/v1/skills/skill/Mining",
    headers=HEADERS,
    params={"character_id": "char-miner"}
)
print(response.json())
# {"name": "Mining", "level": 1, "xp": 0, "tier": "bronze", ...}

# Mine copper ore (level 1 action)
response = requests.post(
    f"{BASE_URL}/api/v1/skills/perform-action",
    headers=HEADERS,
    json={
        "session_id": "training-001",
        "character_id": "char-miner",
        "skill_name": "Mining",
        "action_name": "mine_copper",
        "quantity": 10
    }
)
print(response.json())
# Gains 170 XP (17 XP per ore), levels up to 2 or 3

# Try iron ore (requires level 15)
response = requests.post(
    f"{BASE_URL}/api/v1/skills/perform-action",
    headers=HEADERS,
    json={
        "session_id": "training-001",
        "character_id": "char-miner",
        "skill_name": "Mining",
        "action_name": "mine_iron",
        "quantity": 5
    }
)
# Returns: "Level 15 Mining required (you are level 3)"

# Check skill overview
response = requests.get(
    f"{BASE_URL}/api/v1/skills/overview",
    headers=HEADERS,
    params={"character_id": "char-miner"}
)
print(response.json())
# Shows all 24 skills, total level, combat level
```

### Example 2: Progressive Skill Check

```python
# Attempt to mine a difficult vein
response = requests.post(
    f"{BASE_URL}/api/v1/skills/progressive-check",
    headers=HEADERS,
    json={
        "session_id": "training-001",
        "character_id": "char-miner",
        "skill_name": "Mining",
        "difficulty": 25,
        "use_random": true
    }
)

check_result = response.json()
if check_result["success"]:
    # Success! Can mine the vein
    success_rate = check_result["data"]["success_rate_percent"]
    print(f"Success with {success_rate}% chance")
    
    # Award XP for successful mine
    requests.post(
        f"{BASE_URL}/api/v1/skills/add-xp",
        headers=HEADERS,
        json={
            "session_id": "training-001",
            "character_id": "char-miner",
            "skill_name": "Mining",
            "xp_amount": 50,
            "reason": "Mined difficult vein"
        }
    )
else:
    print("Failed to mine the vein")
```

### Example 3: Checking Item Requirements

```python
# Check if character can equip mithril pickaxe
response = requests.post(
    f"{BASE_URL}/api/v1/skills/check-requirements",
    headers=HEADERS,
    json={
        "character_id": "char-miner",
        "requirements": [
            {
                "skill_name": "Mining",
                "level_required": 50,
                "optional": false
            }
        ]
    }
)

if response.json()["success"]:
    print("Can equip mithril pickaxe!")
else:
    print("Need level 50 Mining")
    # Show current level
    requirements = response.json()["data"]["requirements"]
    for req in requirements:
        print(f"{req['skill']}: {req['current']}/{req['required']}")
```

### Example 4: Combat Level Calculation

```python
# Get overview which includes combat level
response = requests.get(
    f"{BASE_URL}/api/v1/skills/overview",
    headers=HEADERS,
    params={"character_id": "char-warrior"}
)

data = response.json()
print(f"Total Level: {data['total_level']}")
print(f"Combat Level: {data['combat_level']}")

# Combat level is calculated from:
# Base = 0.25 * (Defence + Hitpoints + Prayer/2)
# Melee = 0.325 * (Attack + Strength)
# Ranged = 0.325 * (Ranged/2 + Ranged)
# Magic = 0.325 * (Magic/2 + Magic)
# Combat Level = Base + max(Melee, Ranged, Magic)
```

### Example 5: Tier Progression

```python
# Mine with different tiers
character_id = "char-miner"

# Get current tier
response = requests.get(
    f"{BASE_URL}/api/v1/skills/skill/Mining",
    headers=HEADERS,
    params={"character_id": character_id}
)

skill_data = response.json()
current_tier = skill_data["current_tier"]
next_tier = skill_data["next_tier"]

print(f"Current tier: {current_tier}")
if next_tier:
    print(f"Next tier: {next_tier['name']} at level {next_tier['level_required']}")
    levels_needed = next_tier["level_required"] - skill_data["level"]
    print(f"Need {levels_needed} more levels!")

# Get all accessible tiers
accessible_tiers = skill_data["accessible_tiers"]
print("Can use equipment from tiers:")
for tier in accessible_tiers:
    print(f"  - {tier['name']}")
```

## Skill Progression Tips

### Fast Leveling (1-30)
- Focus on low-level actions with high success rates
- Bronze tier actions provide quick XP early
- Each level-up dramatically increases next level's requirement

### Mid-Game (30-60)
- Steel and Mithril tiers unlock
- Success rates stabilize
- Higher XP actions become more efficient
- Consider alternating skills for variety

### Late Game (60-99)
- Adamant and Rune tiers
- Focus on high-XP actions
- Level-ups become significantly slower
- Total level becomes meaningful metric

### Endgame (99+)
- Dragon tier equipment
- 120 level cap for completionists
- Extremely high XP requirements
- Max efficiency needed for progress

## Integration with Other Systems

### Equipment System
- Tier requirements on weapons/armor
- Higher skill levels unlock better equipment
- Equipment effectiveness scales with tier

### Crafting System
- Skills required to craft items
- Higher levels create better quality
- Recipes unlock at specific levels

### Combat System
- Combat skills affect attack and defense
- Critical hit chances scale with level
- Special abilities unlock at milestones

### World System
- Agility affects movement speed
- Mining/Woodcutting for resource gathering in world
- Skills enable accessing certain areas

### NPC System
- NPCs can teach skills
- Quest requirements based on skill levels
- Trading unlocks based on skills

## Event Types

The skills system generates these event types:

- `skill_xp_gained` - XP added to skill
- `skill_level_up` - Skill increased a level
- `progressive_skill_check` - Progressive check performed
- `skill_action_performed` - Skill training action completed

All events are recorded in the event sourcing log for complete history.

## Customization

### Adding Custom Skills

```python
# In endpoints_skills.py, add to DEFAULT_SKILLS
DEFAULT_SKILLS["CustomSkill"] = SkillCategory.SUPPORT

# Skills auto-initialize on character load
```

### Custom Actions

```python
# Define custom skill actions
skill_actions = {
    "CustomSkill": {
        "custom_action": SkillAction(
            skill_name="CustomSkill",
            action_name="custom_action",
            base_xp=50,
            level_required=10,
            success_rate_base=0.7,
            duration=5.0
        )
    }
}
```

### Custom Tiers

```python
# Add custom tier
TIERS.append(SkillTier(
    name="legendary",
    level_required=110,
    color="#FFD700",
    multiplier=3.0,
    description="Legendary tier equipment"
))
```

## See Also

- [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) - Enhanced RPG features
- [WORLD_GUIDE.md](WORLD_GUIDE.md) - World and movement system
- [NPC_GUIDE.md](NPC_GUIDE.md) - NPC management
- [API_README.md](API_README.md) - Complete API reference

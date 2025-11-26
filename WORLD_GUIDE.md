# World Coordinates, Movement, Actions & Skills Guide

Complete guide for world coordinates, character movement, actions, and skill systems in the Bastards Blood RPG API.

## Overview

The world system provides:
- **3D World Coordinates** - X, Y, Z positioning with regions and areas
- **Movement System** - 10 movement types with realistic mechanics
- **Skill System** - D20-based skill checks with advantage/disadvantage
- **Action System** - Comprehensive action types for interactions
- **Spatial Queries** - Distance calculations and nearby entity detection

## World Coordinates

### Coordinate System

Characters and objects exist in a 3D coordinate space:

```python
{
  "x": 100.5,      # X coordinate
  "y": 250.0,      # Y coordinate
  "z": 0.0,        # Z coordinate (elevation)
  "region": "forest_region",  # Optional region name
  "area": "clearing"          # Optional specific area
}
```

### Location Information

Complete location includes coordinates plus context:

```python
{
  "coordinates": {
    "x": 100, "y": 250, "z": 0,
    "region": "forest", "area": "clearing"
  },
  "facing": 45,  # Direction in degrees (0-359)
  "terrain": "forest",
  "elevation_name": "ground_level",
  "landmarks": ["ancient_tree", "stone_circle"],
  "description": "A peaceful clearing in the dense forest"
}
```

## Movement System

### Movement Types

10 movement types with different speeds and stamina costs:

| Movement Type | Speed Multiplier | Stamina Cost | Description |
|--------------|------------------|--------------|-------------|
| **walk** | 1.0x | 0.1 per unit | Standard walking pace |
| **run** | 2.0x | 0.3 per unit | Running speed |
| **sprint** | 3.0x | 0.6 per unit | Maximum speed |
| **sneak** | 0.5x | 0.15 per unit | Slow, stealthy |
| **crawl** | 0.25x | 0.2 per unit | Very slow, low profile |
| **swim** | 0.8x | 0.4 per unit | Swimming through water |
| **fly** | 2.5x | 0.5 per unit | Flying (requires ability) |
| **climb** | 0.6x | 0.5 per unit | Climbing vertical surfaces |
| **jump** | 1.5x | 0.3 per unit | Jumping across gaps |
| **teleport** | ∞ | 0.0 | Instant travel (magic) |

### Movement Mechanics

**Automatic Calculations:**
- Distance (3D Euclidean)
- Travel duration (based on speed)
- Stamina cost (based on distance and type)
- Path recording (waypoints)

**Example Movement:**
```bash
curl -X POST "http://localhost:8000/api/v1/world/move" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "character_id": "char-hero",
    "destination": {
      "x": 150,
      "y": 300,
      "z": 0,
      "region": "forest"
    },
    "movement_type": "run",
    "auto_path": true
  }'
```

**Response:**
```json
{
  "success": true,
  "event_id": "evt-123",
  "message": "Moved 180.28 units via run",
  "result": {
    "distance": 180.28,
    "duration": 3.0,
    "stamina_cost": 54.08,
    "destination": {"x": 150, "y": 300, "z": 0}
  }
}
```

### Teleportation

Instant travel with no movement mechanics:

```bash
curl -X POST "http://localhost:8000/api/v1/world/teleport" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "character_id": "char-hero",
    "destination": {"x": 500, "y": 500, "z": 100},
    "reason": "magic_portal"
  }'
```

## Skill System

### D20 Skill Checks

Standard D&D-style skill checks with:
- D20 roll
- Skill modifiers
- Difficulty class (DC)
- Advantage/disadvantage
- Critical success/failure

### Skill Check Example

```bash
curl -X POST "http://localhost:8000/api/v1/world/skill-check" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "character_id": "char-hero",
    "skill_name": "Stealth",
    "difficulty": 15,
    "advantage": false,
    "disadvantage": false,
    "context": "sneaking past guards"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Stealth check: 14 + 5 = 19 vs DC 15 - Success!",
  "result": {
    "roll": 14,
    "modifier": 5,
    "total": 19,
    "difficulty": 15,
    "success": true,
    "critical": false,
    "critical_fail": false
  }
}
```

### Advantage & Disadvantage

**Advantage** - Roll twice, take higher:
```json
{
  "advantage": true,
  "roll_text": "Advantage: 8, 16 -> 16"
}
```

**Disadvantage** - Roll twice, take lower:
```json
{
  "disadvantage": true,
  "roll_text": "Disadvantage: 18, 5 -> 5"
}
```

### Learning Skills

**Gain XP in skills:**
```bash
curl -X POST "http://localhost:8000/api/v1/world/learn-skill" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "character_id": "char-hero",
    "skill_name": "Lockpicking",
    "xp_gain": 50,
    "instant_level": false
  }'
```

**Skill Progression:**
- 100 XP for level 1
- Increasing XP per level (100 + level * 10)
- Automatic level-ups when enough XP

## Action System

### Action Types

**Movement:**
- `move` - Standard movement
- `teleport` - Instant travel

**Interaction:**
- `interact` - General interaction
- `use` - Use an object
- `examine` - Examine closely
- `search` - Search for items
- `open`/`close` - Doors, containers
- `lock`/`unlock` - Locked objects

**Combat:**
- `attack` - Attack action
- `defend` - Defensive stance
- `dodge` - Dodge attempt
- `parry` - Parry attack

**Skills:**
- `skill_check` - Skill check
- `cast_spell` - Cast magic
- `use_ability` - Use special ability

**Social:**
- `talk` - Conversation
- `persuade` - Persuasion attempt
- `intimidate` - Intimidation
- `deceive` - Deception

**Other:**
- `rest` - Rest/recover
- `craft` - Crafting
- `gather` - Gather resources
- `custom` - Custom action

### Performing Actions

```bash
curl -X POST "http://localhost:8000/api/v1/world/action" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "actor_id": "char-hero",
    "action_type": "search",
    "target_location": {"x": 100, "y": 200, "z": 0},
    "skill_check": {
      "skill_name": "Investigation",
      "difficulty": 12,
      "modifier": 3
    },
    "duration": 30,
    "cost": {"stamina": 5},
    "data": {"area": "desk_drawers"}
  }'
```

### Interact with Objects

```bash
curl -X POST "http://localhost:8000/api/v1/world/interact" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "actor_id": "char-hero",
    "target_id": "door-001",
    "interaction_type": "open",
    "skill_check": {
      "skill_name": "Athletics",
      "difficulty": 10,
      "modifier": 4
    },
    "data": {"force_open": true}
  }'
```

## API Endpoints

### Movement Endpoints

#### Move Character
```
POST /api/v1/world/move
```
Move character with automatic distance, duration, and cost calculations.

**Parameters:**
- `session_id` - Session ID
- `character_id` - Character/NPC ID
- `destination` - Target coordinates (x, y, z)
- `movement_type` - walk, run, sprint, sneak, etc.
- `auto_path` - Calculate optimal path

#### Teleport
```
POST /api/v1/world/teleport
```
Instant teleportation with no travel time.

#### Update Location
```
POST /api/v1/world/update-location
```
Directly set location (GM/admin use).

### Skill Endpoints

#### Perform Skill Check
```
POST /api/v1/world/skill-check
```
Roll D20 skill check with modifiers.

**Features:**
- Advantage/disadvantage
- Automatic critical success/failure (nat 20/1)
- Character skill bonuses applied

#### Learn Skill
```
POST /api/v1/world/learn-skill
```
Add XP to skill or instantly level up.

**Parameters:**
- `skill_name` - Skill to learn
- `xp_gain` - XP to add
- `instant_level` - Skip XP, level immediately

### Action Endpoints

#### Perform Action
```
POST /api/v1/world/action
```
Execute general game action with optional skill check.

#### Interact
```
POST /api/v1/world/interact
```
Interact with specific object or entity.

### Utility Endpoints

#### Calculate Distance
```
GET /api/v1/world/distance?x1=0&y1=0&z1=0&x2=100&y2=100&z2=0
```
Calculate distance between two points.

**Returns:**
- `distance_3d` - 3D Euclidean distance
- `distance_2d` - 2D distance (ignoring Z)

#### Get Nearby Entities
```
GET /api/v1/world/nearby?session_id=game-001&x=100&y=200&z=0&radius=50
```
Find all entities within radius of coordinates.

#### Get Movement Types
```
GET /api/v1/world/movement-types
```
List all movement types with speed and cost info.

#### Get Action Types
```
GET /api/v1/world/action-types
```
List all available action types by category.

## Integration Examples

### Example 1: Stealth Mission

```python
import requests

BASE_URL = "http://localhost:8000"
HEADERS = {"X-API-Key": "your-secret-key"}

# Sneak to target location
response = requests.post(
    f"{BASE_URL}/api/v1/world/move",
    headers=HEADERS,
    json={
        "session_id": "mission-001",
        "character_id": "char-rogue",
        "destination": {"x": 500, "y": 300, "z": 0},
        "movement_type": "sneak"
    }
)
print(f"Sneaked {response.json()['result']['distance']} units")

# Stealth check to avoid detection
stealth_check = requests.post(
    f"{BASE_URL}/api/v1/world/skill-check",
    headers=HEADERS,
    json={
        "session_id": "mission-001",
        "character_id": "char-rogue",
        "skill_name": "Stealth",
        "difficulty": 15,
        "advantage": True  # In shadows
    }
)

if stealth_check.json()['result']['success']:
    print("Undetected!")
else:
    print("Spotted by guards!")

# Pick lock
lockpick = requests.post(
    f"{BASE_URL}/api/v1/world/interact",
    headers=HEADERS,
    json={
        "session_id": "mission-001",
        "actor_id": "char-rogue",
        "target_id": "vault-door",
        "interaction_type": "unlock",
        "skill_check": {
            "skill_name": "Lockpicking",
            "difficulty": 18,
            "modifier": 6
        }
    }
)

if lockpick.json()['result']['skill_check']['success']:
    print("Lock picked!")
```

### Example 2: Combat Movement

```python
# Sprint to cover
sprint = requests.post(
    f"{BASE_URL}/api/v1/world/move",
    headers=HEADERS,
    json={
        "session_id": "battle-001",
        "character_id": "char-warrior",
        "destination": {"x": 200, "y": 150, "z": 0, "area": "behind_boulder"},
        "movement_type": "sprint"
    }
)

# Athletics check to dive for cover
dive = requests.post(
    f"{BASE_URL}/api/v1/world/skill-check",
    headers=HEADERS,
    json={
        "session_id": "battle-001",
        "character_id": "char-warrior",
        "skill_name": "Athletics",
        "difficulty": 12
    }
)

if dive.json()['result']['success']:
    print("Made it to cover!")
```

### Example 3: Exploration

```python
# Walk to new area
walk = requests.post(
    f"{BASE_URL}/api/v1/world/move",
    headers=HEADERS,
    json={
        "session_id": "explore-001",
        "character_id": "char-explorer",
        "destination": {"x": 1000, "y": 1000, "z": 50, "region": "mountains"},
        "movement_type": "walk"
    }
)

# Search for secrets
search = requests.post(
    f"{BASE_URL}/api/v1/world/action",
    headers=HEADERS,
    json={
        "session_id": "explore-001",
        "actor_id": "char-explorer",
        "action_type": "search",
        "target_location": {"x": 1000, "y": 1000, "z": 50},
        "skill_check": {
            "skill_name": "Investigation",
            "difficulty": 15,
            "modifier": 4
        },
        "duration": 60
    }
)

# Examine interesting finding
if search.json()['result']['skill_check']['success']:
    examine = requests.post(
        f"{BASE_URL}/api/v1/world/action",
        headers=HEADERS,
        json={
            "session_id": "explore-001",
            "actor_id": "char-explorer",
            "action_type": "examine",
            "target_id": "ancient-rune",
            "skill_check": {
                "skill_name": "History",
                "difficulty": 18,
                "modifier": 5
            }
        }
    )
```

### Example 4: Skill Training

```python
# Practice lockpicking
for i in range(5):
    practice = requests.post(
        f"{BASE_URL}/api/v1/world/learn-skill",
        headers=HEADERS,
        json={
            "session_id": "training-001",
            "character_id": "char-rogue",
            "skill_name": "Lockpicking",
            "xp_gain": 25
        }
    )
    
    result = practice.json()['result']
    print(f"Lockpicking: Level {result['level']}, XP: {result['xp']}")
    
    if result['level_up']:
        print("Leveled up!")
```

## Character Location Schema

Add location tracking to characters:

```json
{
  "id": "char-hero",
  "name": "Hero",
  "location": {
    "coordinates": {
      "x": 100,
      "y": 200,
      "z": 0,
      "region": "starting_town",
      "area": "market_square"
    },
    "facing": 90,
    "terrain": "urban",
    "landmarks": ["fountain", "merchant_stall"]
  },
  "movement_speeds": {
    "base_speed": 30,
    "walk_speed": 30,
    "run_speed": 60,
    "sprint_speed": 90
  },
  "skills": {
    "Stealth": {"level": 5, "xp": 50, "bonus": 2},
    "Athletics": {"level": 3, "xp": 75, "bonus": 1},
    "Investigation": {"level": 4, "xp": 25, "bonus": 2}
  }
}
```

## NPC Location Schema

NPCs use the same location system:

```json
{
  "id": "npc-merchant",
  "name": "Shop Owner",
  "location": {
    "coordinates": {"x": 105, "y": 205, "z": 0, "area": "shop"},
    "home_location": "merchant_shop"
  },
  "schedule": {
    "enabled": true,
    "activities": [
      {
        "time": "08:00",
        "location": "shop",
        "activity": "open_shop",
        "duration": 480
      }
    ]
  }
}
```

## Event Sourcing

All movement, skills, and actions recorded as events:

**Event Types:**
- `character_move` - Character movement
- `character_teleport` - Teleportation
- `skill_check` - Skill check performed
- `skill_learn` - Learned new skill
- `skill_level_up` - Skill leveled up
- `skill_xp_gain` - Gained skill XP
- `action_*` - Various action types
- `world_interaction` - Object interaction
- `location_update` - Location changed

## Best Practices

1. **Coordinate System** - Use consistent coordinate system across game
2. **Movement Speed** - Balance speeds for gameplay
3. **Stamina Management** - Track stamina costs realistically
4. **Skill Progression** - Make skill leveling meaningful
5. **Terrain Effects** - Apply terrain modifiers to movement
6. **Line of Sight** - Check distance for visibility
7. **Pathfinding** - Use auto-path for complex navigation
8. **Skill Difficulty** - Set appropriate DCs for skill checks

## Advanced Features

### Terrain Modifiers

Apply modifiers based on terrain:
- **Plains** - Normal speed
- **Forest** - -20% speed, +bonus to Stealth
- **Mountain** - -40% speed, climbing required
- **Desert** - +stamina cost
- **Water** - Swim speed, high stamina
- **Urban** - Normal speed, easy navigation

### Zone Management

Define game zones with boundaries:
```json
{
  "id": "zone-forest",
  "name": "Dark Forest",
  "bounds": {
    "min_x": 0, "max_x": 1000,
    "min_y": 0, "max_y": 1000,
    "min_z": 0, "max_z": 100
  },
  "terrain": "forest",
  "level_range": {"min": 5, "max": 10},
  "poi": [
    {"name": "Ancient Tree", "x": 500, "y": 500},
    {"name": "Hidden Grove", "x": 750, "y": 250}
  ]
}
```

### Skill Categories

Organize skills by type:
- **Physical**: Athletics, Acrobatics, Stealth
- **Mental**: Investigation, History, Arcana
- **Social**: Persuasion, Deception, Intimidation
- **Craft**: Lockpicking, Engineering, Alchemy

## See Also

- [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) - Character features
- [NPC_GUIDE.md](NPC_GUIDE.md) - NPC management
- [API_README.md](API_README.md) - Core API docs

# World Builder Guide - Extensive World System

## Overview

The World Builder system provides comprehensive tools for creating an extensive, dynamic game world where players can:
- Gather resources from various nodes (mining, woodcutting, fishing, etc.)
- Train skills in dedicated areas with XP bonuses
- Craft items at specialized stations
- Fight NPCs in combat zones
- Explore diverse regions and environments

Admins can build and modify the world **in real-time** while the game is running, creating a living, evolving world.

## Architecture

### World Structure Hierarchy

```
World
└── Regions (terrain, level ranges, PvP rules)
    ├── Resource Nodes (gathering points)
    ├── Skill Areas (training grounds)
    ├── Crafting Stations (forges, workbenches, etc.)
    └── NPC Zones (combat areas)
```

## Admin Tools - Real-Time World Building

### Creating Regions

Regions are the foundation of the world. Each region can have its own terrain, level requirements, and ruleset.

**Endpoint:** `POST /api/v1/world-builder/admin/region/create`

**Example Request:**
```json
{
  "admin_id": "admin-1",
  "name": "Lumbridge",
  "description": "A peaceful starting town with low-level resources and training areas",
  "terrain_type": "plains",
  "center_x": 3222.0,
  "center_y": 3222.0,
  "center_z": 0.0,
  "radius": 200.0,
  "min_level": 1,
  "max_level": 20,
  "pvp_enabled": false,
  "safe_zone": true,
  "weather": "clear",
  "time_of_day": "day"
}
```

**Terrain Types:**
- `plains` - Open grasslands, easy traversal
- `forest` - Woodcutting resources, limited visibility
- `mountain` - Mining resources, climbing required
- `desert` - Harsh environment, water needed
- `water` - Fishing areas, swimming required
- `swamp` - Slow movement, unique resources
- `urban` - Cities and towns, NPCs and shops
- `dungeon` - Underground areas, high-level content
- `cave` - Mining and exploration
- `road` - Fast travel routes
- `custom` - Custom terrain with unique properties

### Creating Resource Nodes

Resource nodes are gathering points where players can collect materials and gain skill XP.

**Endpoint:** `POST /api/v1/world-builder/admin/resource/create`

**Mining Node Example:**
```json
{
  "admin_id": "admin-1",
  "region_id": "region-123",
  "name": "Iron Ore Vein",
  "resource_type": "mining",
  "skill_required": "Mining",
  "level_required": 15,
  "x": 3250.0,
  "y": 3200.0,
  "z": 0.0,
  "resources": ["iron_ore", "clay", "copper_ore"],
  "xp_per_gather": 35,
  "gather_time": 3.0,
  "respawn_time": 45.0,
  "max_capacity": 150,
  "depletion_rate": 1,
  "quality_range": [1, 100],
  "rare_drop_chance": 0.08,
  "description": "A rich vein of iron ore, occasionally containing copper and clay"
}
```

**Woodcutting Node Example:**
```json
{
  "admin_id": "admin-1",
  "region_id": "region-123",
  "name": "Oak Tree",
  "resource_type": "woodcutting",
  "skill_required": "Woodcutting",
  "level_required": 15,
  "x": 3245.0,
  "y": 3215.0,
  "z": 0.0,
  "resources": ["oak_logs", "bird_nest"],
  "xp_per_gather": 37.5,
  "gather_time": 4.0,
  "respawn_time": 60.0,
  "max_capacity": 100,
  "depletion_rate": 1,
  "quality_range": [10, 90],
  "rare_drop_chance": 0.05,
  "description": "A sturdy oak tree that yields valuable logs"
}
```

**Fishing Spot Example:**
```json
{
  "admin_id": "admin-1",
  "region_id": "region-123",
  "name": "Salmon Fishing Spot",
  "resource_type": "fishing",
  "skill_required": "Fishing",
  "level_required": 30,
  "x": 3240.0,
  "y": 3210.0,
  "z": 0.0,
  "resources": ["salmon", "trout", "seaweed"],
  "xp_per_gather": 50,
  "gather_time": 5.0,
  "respawn_time": 0.0,
  "max_capacity": 999999,
  "depletion_rate": 0,
  "quality_range": [20, 100],
  "rare_drop_chance": 0.03,
  "description": "A fishing spot known for salmon"
}
```

**Resource Types:**
- `mining` - Ore and stone extraction
- `woodcutting` - Tree felling and log gathering
- `fishing` - Catching fish and aquatic resources
- `farming` - Crop and plant cultivation
- `herb_gathering` - Herb and plant collection
- `hunting` - Animal tracking and harvesting
- `foraging` - Wild food and material gathering
- `quarrying` - Stone block extraction
- `excavation` - Archaeological digging
- `custom` - Custom resource gathering

### Creating Skill Training Areas

Skill areas provide XP bonuses and specialized training activities for specific skills.

**Endpoint:** `POST /api/v1/world-builder/admin/skill-area/create`

**Combat Training Ground Example:**
```json
{
  "admin_id": "admin-1",
  "region_id": "region-123",
  "name": "Lumbridge Combat Academy",
  "area_type": "training_ground",
  "skills_trained": ["Attack", "Strength", "Defence"],
  "x": 3220.0,
  "y": 3220.0,
  "z": 0.0,
  "radius": 75.0,
  "xp_bonus": 1.25,
  "level_requirements": {
    "Attack": 1,
    "Strength": 1,
    "Defence": 1
  },
  "access_cost": 0,
  "activities": [
    "Train with dummies",
    "Spar with trainers",
    "Complete combat challenges"
  ],
  "npcs": ["combat_instructor", "weapon_master"],
  "description": "A safe training area for learning combat basics"
}
```

**Magic Academy Example:**
```json
{
  "admin_id": "admin-1",
  "region_id": "region-124",
  "name": "Wizards' Tower",
  "area_type": "magic_academy",
  "skills_trained": ["Magic", "Runecraft"],
  "x": 3100.0,
  "y": 3150.0,
  "z": 2.0,
  "radius": 100.0,
  "xp_bonus": 1.5,
  "level_requirements": {
    "Magic": 10
  },
  "access_cost": 100,
  "activities": [
    "Study spell books",
    "Practice magic",
    "Craft runes",
    "Take magic exams"
  ],
  "npcs": ["archmage", "rune_apprentice", "magic_tutor"],
  "description": "An advanced academy for magical studies"
}
```

**Area Types:**
- `training_ground` - General skill training
- `combat_arena` - PvP and combat practice
- `crafting_hall` - Crafting skill workshops
- `magic_academy` - Magic and spellcasting
- `thieves_guild` - Thieving and stealth skills
- `monastery` - Prayer and meditation
- `library` - Lore and knowledge skills
- `dungeon` - High-level skill training
- `wilderness` - Survival and outdoor skills
- `custom` - Custom training areas

### Creating Crafting Stations

Crafting stations allow players to create items with bonuses based on the station quality.

**Endpoint:** `POST /api/v1/world-builder/admin/crafting-station/create`

**Forge Example:**
```json
{
  "admin_id": "admin-1",
  "region_id": "region-123",
  "name": "Master Forge",
  "station_type": "forge",
  "x": 3230.0,
  "y": 3225.0,
  "z": 0.0,
  "crafting_skills": ["Smithing"],
  "level_bonus": 5,
  "speed_bonus": 1.2,
  "quality_bonus": 10,
  "special_recipes": [
    "legendary_sword",
    "dragonplate_armor",
    "masterwork_shield"
  ],
  "requirements": {
    "Smithing": 50
  },
  "usage_cost": 50,
  "max_tier": 8,
  "description": "A legendary forge capable of crafting the finest weapons and armor"
}
```

**Alchemy Lab Example:**
```json
{
  "admin_id": "admin-1",
  "region_id": "region-125",
  "name": "Advanced Alchemy Laboratory",
  "station_type": "alchemy_lab",
  "x": 2900.0,
  "y": 3400.0,
  "z": 1.0,
  "crafting_skills": ["Herblore", "Magic"],
  "level_bonus": 3,
  "speed_bonus": 1.3,
  "quality_bonus": 8,
  "special_recipes": [
    "super_restore_potion",
    "grand_magic_potion",
    "philosopher_stone"
  ],
  "requirements": {
    "Herblore": 40,
    "Magic": 30
  },
  "usage_cost": 100,
  "max_tier": 7,
  "description": "A sophisticated laboratory for brewing powerful potions"
}
```

**Station Types:**
- `forge` - Metalworking and weapon/armor smithing
- `anvil` - Basic metalworking
- `workbench` - General crafting and construction
- `alchemy_lab` - Potion brewing and transmutation
- `enchanting_table` - Item enchanting and magic imbuing
- `cooking_station` - Food preparation
- `sewing_table` - Textile and leather crafting
- `fletching_table` - Bow and arrow crafting
- `jewelers_bench` - Jewelry crafting
- `tannery` - Leather working
- `custom` - Custom crafting stations

### Creating NPC Combat Zones

NPC zones automatically spawn enemies for players to fight, providing combat XP and loot.

**Endpoint:** `POST /api/v1/world-builder/admin/npc-zone/create`

**Low-Level Zone Example:**
```json
{
  "admin_id": "admin-1",
  "region_id": "region-123",
  "name": "Goblin Village",
  "center_x": 3260.0,
  "center_y": 3240.0,
  "center_z": 0.0,
  "radius": 80.0,
  "npc_types": ["goblin", "goblin_guard"],
  "spawn_rate": 20.0,
  "max_npcs": 8,
  "min_level": 2,
  "max_level": 8,
  "aggressive": true,
  "combat_xp_bonus": 1.0,
  "loot_bonus": 1.0,
  "boss_spawn_chance": 0.01,
  "boss_templates": ["goblin_chief"],
  "description": "A dangerous area inhabited by aggressive goblins"
}
```

**High-Level Dungeon Example:**
```json
{
  "admin_id": "admin-1",
  "region_id": "region-130",
  "name": "Ancient Dragon Lair",
  "center_x": 4500.0,
  "center_y": 4500.0,
  "center_z": -50.0,
  "radius": 150.0,
  "npc_types": ["dragon_whelp", "dragon_guard", "elder_dragon"],
  "spawn_rate": 60.0,
  "max_npcs": 5,
  "min_level": 80,
  "max_level": 100,
  "aggressive": true,
  "combat_xp_bonus": 2.0,
  "loot_bonus": 3.0,
  "boss_spawn_chance": 0.15,
  "boss_templates": ["ancient_dragon", "dragon_king"],
  "description": "A treacherous lair filled with powerful dragons and legendary treasure"
}
```

## Player Actions

### Gathering Resources

Players can gather resources from nodes to gain materials and XP.

**Endpoint:** `POST /api/v1/world-builder/gather`

**Request:**
```json
{
  "session_id": "session-abc123",
  "character_id": "char-1",
  "node_id": "resource-iron-vein-1"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Gathered iron_ore (quality: 75) and found rare iron_bar! (+35 Mining XP)",
  "data": {
    "resource": "iron_ore",
    "quality": 75,
    "rare_drop": "iron_bar",
    "xp_gained": 35,
    "skill": "Mining",
    "new_skill_xp": 1250
  },
  "timestamp": "2025-11-26T08:30:00.000Z"
}
```

**Mechanics:**
- Requires appropriate skill level
- Node capacity depletes with each gather
- Quality determined by player level vs requirement
- Chance for rare drops
- XP granted to relevant skill
- Node respawns after depletion time

### Finding Nearby Resources

Players can discover resource nodes near their location.

**Endpoint:** `GET /api/v1/world-builder/resources/nearby`

**Parameters:**
- `character_id` - Character making the query
- `session_id` - Active session ID
- `radius` - Search radius (default: 100.0)

**Response:**
```json
{
  "success": true,
  "message": "Found 5 resources within 100.0 units",
  "data": {
    "resources": [
      {
        "id": "resource-1",
        "name": "Iron Ore Vein",
        "type": "mining",
        "skill_required": "Mining",
        "level_required": 15,
        "distance": 45.3,
        "available": true,
        "capacity": "120/150"
      },
      {
        "id": "resource-2",
        "name": "Oak Tree",
        "type": "woodcutting",
        "skill_required": "Woodcutting",
        "level_required": 15,
        "distance": 62.8,
        "available": true,
        "capacity": "85/100"
      }
    ]
  },
  "timestamp": "2025-11-26T08:30:00.000Z"
}
```

## World Query Endpoints

### List All Regions

**Endpoint:** `GET /api/v1/world-builder/regions`

Returns a summary of all regions with their features.

### Get Region Details

**Endpoint:** `GET /api/v1/world-builder/region/{region_id}`

Returns complete details of a region including all resource nodes, skill areas, crafting stations, and NPC zones.

## Real-Time World Modification

Admins can modify world features while the game is running, allowing for:

- **Dynamic Events:** Create temporary resource nodes or NPC invasions
- **Seasonal Changes:** Modify resource availability or spawn rates
- **Live Updates:** Adjust difficulty or loot based on player progression
- **Event Management:** Set up special events or limited-time content
- **Balance Tuning:** Fine-tune XP rates, spawn rates, and rewards on the fly

### Modification Examples

**Increase Resource Spawn Rate:**
```json
{
  "admin_id": "admin-1",
  "target_type": "resource_node",
  "target_id": "resource-iron-vein-1",
  "modifications": {
    "respawn_time": 30.0,
    "xp_per_gather": 50
  },
  "reason": "Double XP weekend event"
}
```

**Create Temporary Boss Spawn:**
```json
{
  "admin_id": "admin-1",
  "target_type": "npc_zone",
  "target_id": "npc-zone-goblin-village",
  "modifications": {
    "boss_spawn_chance": 1.0,
    "boss_templates": ["mega_goblin_king"],
    "loot_bonus": 5.0
  },
  "reason": "Special Halloween event"
}
```

## Integration with Skills System

The world builder integrates seamlessly with the skills system:

1. **Resource nodes** grant XP to gathering skills (Mining, Woodcutting, Fishing, etc.)
2. **Skill areas** provide XP bonuses for training
3. **Crafting stations** allow skill-based item creation
4. **NPC zones** provide combat XP

All skill progression follows the RuneScape-style 120-level system with 7 tiers.

## Integration with Combat System

NPC zones automatically spawn enemies that integrate with the combat system:

- NPCs have health, damage, and defense stats
- Combat follows server-authoritative rules
- XP and loot drops are calculated server-side
- Boss spawns provide epic encounters

## Best Practices for World Building

### Region Design

1. **Start with low-level areas** near spawn points
2. **Create clear progression paths** with increasing level requirements
3. **Balance PvP and safe zones** to accommodate different playstyles
4. **Use terrain types** to create visual and mechanical variety

### Resource Placement

1. **Group similar resources** in thematic areas (mines, forests, lakes)
2. **Vary resource levels** to create progression within regions
3. **Add rare resources** in dangerous or hard-to-reach locations
4. **Balance spawn rates** to prevent overcrowding or shortages

### Skill Area Layout

1. **Place beginner areas** near safe zones
2. **Create specialty areas** for advanced players
3. **Add requirements** to maintain challenge and progression
4. **Include NPCs** for guidance and flavor

### Crafting Station Strategy

1. **Start with basic stations** in starter towns
2. **Add advanced stations** in high-level areas
3. **Create special stations** with unique recipes
4. **Balance usage costs** against rewards

### NPC Zone Management

1. **Match NPC levels** to region level ranges
2. **Vary spawn rates** based on player activity
3. **Add boss spawns** for excitement and rewards
4. **Create themed zones** for variety

## Example: Complete Region Setup

Here's how to set up a complete beginner region:

1. **Create the region** (Lumbridge)
2. **Add resource nodes:**
   - Copper and tin ore veins (Mining 1-10)
   - Normal and oak trees (Woodcutting 1-15)
   - Fishing spots (Fishing 1-20)
3. **Add skill areas:**
   - Combat training ground (Attack/Strength/Defence)
   - Cooking range area (Cooking with bonus)
4. **Add crafting stations:**
   - Bronze forge (Smithing 1-10)
   - Basic workbench (Crafting 1-15)
5. **Add NPC zones:**
   - Chicken farm (Combat level 1-2)
   - Goblin village (Combat level 5-8)
   - Giant rat cellar (Combat level 3-5)

## Server-Side Validation

All world builder actions are validated server-side:

- ✅ Region existence checks
- ✅ Skill level requirements enforced
- ✅ Resource capacity management
- ✅ Cooldown and respawn timers
- ✅ Item ownership verification
- ✅ XP calculations server-side
- ✅ Loot generation server-side

This prevents cheating and ensures a fair, balanced game world.

## Conclusion

The World Builder system provides comprehensive tools for creating an extensive, dynamic game world. With real-time modification capabilities, admins can continuously evolve the world based on player feedback and create engaging events and content updates.

The system supports:
- ✅ Resource gathering with skill progression
- ✅ Dedicated training areas with bonuses
- ✅ Specialized crafting stations
- ✅ Dynamic NPC combat zones
- ✅ Real-time world modification
- ✅ Server-authoritative design
- ✅ Complete integration with existing systems

Your game world is now ready for extensive player exploration and engagement!

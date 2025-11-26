# NPC Management System Guide

Comprehensive guide for managing NPCs (Non-Player Characters) in the Bastards Blood RPG API system.

## Overview

The NPC management system provides complete control over all types of NPCs, from merchants and quest-givers to enemies and companions. NPCs are fully integrated with all existing systems including inventory, equipment, abilities, combat, and relationships.

## NPC Types

The system supports 13 pre-defined NPC types, plus custom types:

- **merchant** - Buys and sells items, focused on trading
- **enemy** - Hostile NPC, will attack on sight
- **ally** - Friendly NPC, may help in combat
- **neutral** - Neither hostile nor friendly
- **quest_giver** - Provides quests to players
- **guard** - Protects areas, enforces rules
- **companion** - Can join player party
- **boss** - Powerful enemy, usually unique
- **vendor** - Specialized merchant (weapons, armor, potions, etc.)
- **trainer** - Teaches skills or abilities
- **innkeeper** - Manages inn/tavern services
- **blacksmith** - Repairs and crafts items
- **custom** - Define your own NPC type

## Core Features

### 1. Complete Character System
NPCs use the same comprehensive character system as players:
- Stats (STR, DEX, CON, INT, WIS, CHA)
- Attributes (armor_class, speed, initiative, etc.)
- HP with temp HP support
- Resources (mana, stamina, etc.)
- Inventory with detailed items
- Equipment with 15+ slots
- Abilities and spells
- Status effects

### 2. Behavior System
Define how NPCs act:
```json
{
  "behavior": {
    "aggression": "aggressive",  // passive, defensive, neutral, aggressive, hostile
    "disposition": "unfriendly",  // friendly, neutral, unfriendly, hostile
    "wander": true,
    "patrol_route": ["town_square", "market", "tavern"],
    "flee_threshold": 30,  // Flee at 30% HP
    "call_for_help": true
  }
}
```

### 3. Dialogue System
Multiple dialogue categories with context-aware responses:
```json
{
  "dialogue": {
    "greeting": [
      "Well met, traveler!",
      "What brings you here?",
      "Greetings."
    ],
    "farewell": [
      "Safe travels!",
      "Until we meet again."
    ],
    "trade": [
      "Looking to buy or sell?",
      "I have the finest wares in the land!"
    ],
    "combat": [
      "You'll regret that!",
      "For honor!"
    ],
    "custom": {
      "quest_complete": ["Well done! Here's your reward."],
      "low_reputation": ["I don't trust you."]
    }
  }
}
```

### 4. Trading System
Full trading support with price modifiers:
```json
{
  "trade": {
    "can_trade": true,
    "buy_rate": 1.5,  // Player pays 150% when buying
    "sell_rate": 0.5,  // Player gets 50% when selling
    "currency": {
      "gold": 500,
      "silver": 1000
    },
    "trade_inventory": ["sword", "shield", "health-potion"],
    "preferred_items": ["gems", "rare-materials"]
  }
}
```

### 5. Quest System
NPCs can give and track quests:
```json
{
  "quest": {
    "can_give_quests": true,
    "active_quests": ["quest-slay-dragon", "quest-find-artifact"],
    "completed_quests": ["quest-help-farmer"]
  }
}
```

### 6. Relationship System
Track relationships with players and other NPCs:
```json
{
  "relationships": {
    "char-hero": {
      "reputation": 75,  // -100 to 100
      "relationship_type": "friend",  // enemy, rival, neutral, acquaintance, friend, ally, family, lover
      "trust_level": 80  // 0-100
    },
    "npc-merchant": {
      "reputation": -20,
      "relationship_type": "rival",
      "trust_level": 30
    }
  }
}
```

### 7. Schedule System
NPCs can follow daily schedules:
```json
{
  "schedule": {
    "enabled": true,
    "activities": [
      {
        "time": "08:00",
        "location": "market_stall",
        "activity": "open_shop",
        "duration": 480
      },
      {
        "time": "16:00",
        "location": "tavern",
        "activity": "socialize",
        "duration": 120
      },
      {
        "time": "20:00",
        "location": "home",
        "activity": "rest",
        "duration": 600
      }
    ]
  }
}
```

### 8. AI System
Configure NPC artificial intelligence:
```json
{
  "ai": {
    "ai_type": "tactical",  // simple, tactical, support, ranged, melee, caster, custom
    "combat_style": "ranged_spellcaster",
    "target_priority": ["healer", "mage", "warrior"],
    "use_abilities": true,
    "use_items": true
  }
}
```

### 9. Location & Spawning
Control where and how NPCs appear:
```json
{
  "location": {
    "area": "town_market",
    "position": {"x": 150.5, "y": 200.0, "z": 0.0},
    "home_location": "merchant_house"
  },
  "spawning": {
    "can_respawn": true,
    "respawn_time": 3600,  // seconds
    "spawn_location": "goblin_cave",
    "spawn_condition": "night_time"
  }
}
```

### 10. Loot System
Define what NPCs drop when defeated:
```json
{
  "loot": {
    "drop_chance": 0.8,  // 80% chance to drop something
    "guaranteed_drops": ["copper-coins"],
    "possible_drops": [
      {
        "item_id": "iron-sword",
        "chance": 0.3,
        "quantity_min": 1,
        "quantity_max": 1
      },
      {
        "item_id": "health-potion",
        "chance": 0.5,
        "quantity_min": 1,
        "quantity_max": 3
      }
    ],
    "currency_drops": {
      "gold": {"min": 10, "max": 50},
      "silver": {"min": 50, "max": 200}
    }
  }
}
```

### 11. Customization
Detailed appearance and voice:
```json
{
  "customization": {
    "appearance": {
      "height": "6'2\"",
      "build": "muscular",
      "hair_color": "black",
      "eye_color": "green",
      "skin_tone": "tan",
      "age": 35,
      "distinctive_features": ["scar on left cheek", "missing finger"]
    },
    "voice": {
      "pitch": "deep",
      "accent": "northern",
      "speech_pattern": "speaks slowly"
    }
  }
}
```

## API Endpoints

### CRUD Operations

#### List NPCs
```bash
GET /api/v1/npcs/
```

**Query Parameters:**
- `npc_type` - Filter by NPC type
- `faction` - Filter by faction
- `min_level` - Minimum level
- `max_level` - Maximum level
- `location` - Filter by location
- `tags` - Filter by tags (can specify multiple)

**Example:**
```bash
curl "http://localhost:8000/api/v1/npcs/?npc_type=merchant&min_level=5" \
  -H "X-API-Key: your-secret-key"
```

#### Get NPC
```bash
GET /api/v1/npcs/{npc_id}
```

#### Create NPC
```bash
POST /api/v1/npcs/
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/npcs/" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "npc": {
      "id": "npc-blacksmith-john",
      "name": "John the Blacksmith",
      "npc_type": "blacksmith",
      "class": "Craftsman",
      "lvl": 8,
      "stats": {"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 12, "CHA": 11},
      "hp": {"max": 60, "current": 60},
      "trade": {
        "can_trade": true,
        "buy_rate": 1.2,
        "sell_rate": 0.6
      },
      "dialogue": {
        "greeting": ["Need some repairs?", "Best smith in town!"],
        "trade": ["I can fix that for you.", "Quality work, fair prices."]
      }
    }
  }'
```

#### Update NPC
```bash
PUT /api/v1/npcs/{npc_id}
```

#### Delete NPC
```bash
DELETE /api/v1/npcs/{npc_id}
```

### Interaction Endpoints

#### NPC Interaction
General interaction endpoint for various interaction types:
```bash
POST /api/v1/npcs/interact
```

**Interaction Types:**
- `talk` - General conversation
- `trade` - Initiate trading
- `quest` - Quest-related interaction
- `attack` - Combat initiation
- `help` - Ask for help
- `follow` - Request to follow
- `examine` - Examine NPC
- Custom types

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/npcs/interact" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "player_id": "char-hero",
    "npc_id": "npc-blacksmith-john",
    "interaction_type": "examine",
    "data": {}
  }'
```

#### NPC Dialogue
Handle dialogue with appropriate responses:
```bash
POST /api/v1/npcs/dialogue
```

**Dialogue Categories:**
- `greeting` - Initial greeting
- `farewell` - Goodbye message
- `trade` - Trading dialogue
- `combat` - Combat taunts
- Custom categories

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/npcs/dialogue" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "player_id": "char-hero",
    "npc_id": "npc-blacksmith-john",
    "dialogue_category": "greeting",
    "player_input": null
  }'
```

#### NPC Trade
Trade with NPCs:
```bash
POST /api/v1/npcs/trade
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/npcs/trade" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "player_id": "char-hero",
    "npc_id": "npc-blacksmith-john",
    "trade_type": "buy",
    "item_id": "iron-sword",
    "quantity": 1
  }'
```

#### NPC Combat
NPC performs combat action:
```bash
POST /api/v1/npcs/combat
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/npcs/combat" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "npc_id": "npc-orc-warrior",
    "target_id": "char-hero",
    "action_type": "melee_attack",
    "data": {
      "weapon": "greataxe",
      "roll": 17
    }
  }'
```

#### Update Relationship
Modify NPC-character relationship:
```bash
POST /api/v1/npcs/relationship
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/npcs/relationship" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "npc_id": "npc-merchant-sarah",
    "character_id": "char-hero",
    "reputation_change": 10,
    "trust_change": 5,
    "new_relationship_type": "friend"
  }'
```

#### Spawn NPC
Spawn an NPC instance in a session:
```bash
POST /api/v1/npcs/spawn
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/npcs/spawn" \
  -H "X-API-Key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "game-001",
    "npc_id": "npc-goblin-scout",
    "location": "forest_path",
    "instance_id": null
  }'
```

#### Get NPC Types
List all available NPC types with descriptions:
```bash
GET /api/v1/npcs/types
```

## Complete NPC Examples

### Example 1: Merchant NPC
```json
{
  "id": "npc-merchant-sarah",
  "name": "Sarah the Merchant",
  "npc_type": "merchant",
  "class": "Trader",
  "race": "Human",
  "lvl": 5,
  "faction": "merchants_guild",
  "stats": {
    "STR": 10,
    "DEX": 12,
    "CON": 11,
    "INT": 14,
    "WIS": 13,
    "CHA": 16
  },
  "attributes": {
    "persuasion": 8,
    "appraisal": 10
  },
  "hp": {
    "max": 35,
    "current": 35
  },
  "inventory": [
    {
      "id": "health-potion",
      "name": "Health Potion",
      "type": "consumable",
      "quantity": 10,
      "value": 50
    },
    {
      "id": "iron-sword",
      "name": "Iron Sword",
      "type": "weapon",
      "quantity": 3,
      "value": 150
    }
  ],
  "behavior": {
    "aggression": "passive",
    "disposition": "friendly",
    "wander": false
  },
  "dialogue": {
    "greeting": [
      "Welcome to my shop!",
      "Looking for something specific?",
      "Best prices in town!"
    ],
    "trade": [
      "What can I get you?",
      "I have excellent deals today!",
      "Quality goods, reasonable prices."
    ],
    "farewell": [
      "Come back soon!",
      "Safe travels!",
      "Thank you for your business!"
    ]
  },
  "trade": {
    "can_trade": true,
    "buy_rate": 1.3,
    "sell_rate": 0.7,
    "currency": {
      "gold": 500,
      "silver": 2000
    },
    "trade_inventory": ["health-potion", "iron-sword", "leather-armor", "rope"],
    "preferred_items": ["gems", "rare-materials", "magic-items"]
  },
  "schedule": {
    "enabled": true,
    "activities": [
      {
        "time": "08:00",
        "location": "market_stall",
        "activity": "open_shop",
        "duration": 540
      },
      {
        "time": "17:00",
        "location": "home",
        "activity": "close_shop",
        "duration": 900
      }
    ]
  },
  "location": {
    "area": "town_market",
    "home_location": "merchant_quarter"
  },
  "tags": ["merchant", "friendly", "quest_available"]
}
```

### Example 2: Boss Enemy NPC
```json
{
  "id": "npc-dragon-vermithrax",
  "name": "Vermithrax the Destroyer",
  "npc_type": "boss",
  "class": "Ancient Dragon",
  "race": "Dragon",
  "lvl": 20,
  "faction": "dragons",
  "stats": {
    "STR": 25,
    "DEX": 14,
    "CON": 23,
    "INT": 16,
    "WIS": 15,
    "CHA": 18
  },
  "attributes": {
    "armor_class": 22,
    "speed": 40,
    "fly_speed": 80,
    "fire_resistance": 100,
    "cold_resistance": -50
  },
  "hp": {
    "max": 500,
    "current": 500
  },
  "resources": {
    "dragon_breath": {
      "max": 3,
      "current": 3
    }
  },
  "abilities": [
    {
      "id": "fire-breath",
      "name": "Fire Breath",
      "type": "ability",
      "cost": {"dragon_breath": 1},
      "cooldown": 3,
      "description": "Breathe a cone of fire dealing massive damage"
    },
    {
      "id": "tail-sweep",
      "name": "Tail Sweep",
      "type": "ability",
      "cost": {},
      "cooldown": 0,
      "description": "Sweep tail to hit all nearby enemies"
    },
    {
      "id": "frightful-presence",
      "name": "Frightful Presence",
      "type": "passive",
      "description": "Enemies must resist fear or flee"
    }
  ],
  "behavior": {
    "aggression": "aggressive",
    "disposition": "hostile",
    "wander": false,
    "flee_threshold": 10,
    "call_for_help": false
  },
  "dialogue": {
    "greeting": [
      "You dare enter my lair?!",
      "Another fool seeking treasure..."
    ],
    "combat": [
      "BURN!",
      "You will be my next meal!",
      "Your bones will decorate my hoard!"
    ]
  },
  "ai": {
    "ai_type": "tactical",
    "combat_style": "breath_weapon_priority",
    "target_priority": ["healer", "ranged", "melee"],
    "use_abilities": true,
    "use_items": false
  },
  "location": {
    "area": "dragon_lair",
    "home_location": "dragon_lair"
  },
  "spawning": {
    "can_respawn": false,
    "respawn_time": null,
    "spawn_location": "dragon_lair",
    "spawn_condition": "none"
  },
  "loot": {
    "drop_chance": 1.0,
    "guaranteed_drops": ["dragon-scales", "dragon-tooth"],
    "possible_drops": [
      {
        "item_id": "legendary-sword",
        "chance": 0.1,
        "quantity_min": 1,
        "quantity_max": 1
      },
      {
        "item_id": "magic-ring",
        "chance": 0.3,
        "quantity_min": 1,
        "quantity_max": 2
      },
      {
        "item_id": "rare-gem",
        "chance": 0.8,
        "quantity_min": 3,
        "quantity_max": 10
      }
    ],
    "currency_drops": {
      "gold": {"min": 1000, "max": 5000},
      "gems": {"min": 10, "max": 50}
    }
  },
  "customization": {
    "appearance": {
      "height": "60 feet long",
      "build": "massive",
      "skin_tone": "crimson scales",
      "age": 500,
      "distinctive_features": ["scarred wings", "missing horn", "glowing eyes"]
    }
  },
  "tags": ["boss", "dragon", "legendary", "fire_type"]
}
```

### Example 3: Companion NPC
```json
{
  "id": "npc-companion-lyra",
  "name": "Lyra Swiftwind",
  "npc_type": "companion",
  "class": "Ranger",
  "race": "Elf",
  "lvl": 7,
  "faction": "forest_guardians",
  "stats": {
    "STR": 14,
    "DEX": 18,
    "CON": 12,
    "INT": 13,
    "WIS": 16,
    "CHA": 14
  },
  "attributes": {
    "armor_class": 16,
    "speed": 35,
    "stealth": 8,
    "perception": 7
  },
  "hp": {
    "max": 55,
    "current": 55
  },
  "resources": {
    "stamina": {"max": 100, "current": 100}
  },
  "equipment": {
    "main_hand": {
      "id": "elven-bow",
      "name": "Elven Longbow",
      "type": "weapon"
    },
    "chest": {
      "id": "leather-armor",
      "name": "Studded Leather Armor",
      "type": "armor"
    }
  },
  "abilities": [
    {
      "id": "hunters-mark",
      "name": "Hunter's Mark",
      "type": "ability",
      "cost": {"stamina": 10},
      "cooldown": 0,
      "description": "Mark target for bonus damage"
    },
    {
      "id": "volley",
      "name": "Volley",
      "type": "ability",
      "cost": {"stamina": 20},
      "cooldown": 2,
      "description": "Fire multiple arrows at once"
    }
  ],
  "behavior": {
    "aggression": "defensive",
    "disposition": "friendly",
    "wander": false,
    "flee_threshold": 20
  },
  "dialogue": {
    "greeting": ["Ready to move out?", "The forest calls to us."],
    "combat": ["I've got your back!", "For nature!"],
    "custom": {
      "encourage": ["You can do this!", "Stay strong!"],
      "warning": ["Watch out!", "Enemies ahead!"]
    }
  },
  "ai": {
    "ai_type": "support",
    "combat_style": "ranged_support",
    "target_priority": ["ranged", "caster", "melee"],
    "use_abilities": true,
    "use_items": true
  },
  "relationships": {
    "char-hero": {
      "reputation": 100,
      "relationship_type": "ally",
      "trust_level": 95
    }
  },
  "tags": ["companion", "ranger", "support", "ranged"]
}
```

## Integration with Existing Systems

### Inventory & Equipment
NPCs use the same inventory and equipment system as player characters:
- Detailed items with properties
- Equipment slots
- Item trading
- Loot drops

### Combat System
NPCs participate fully in combat:
- Use abilities and spells
- AI-driven decision making
- Status effects
- Damage and healing

### Crafting & Trading
NPCs can:
- Sell and buy items
- Craft items (blacksmiths, artisans)
- Teach recipes
- Have preferred items

### Quest System
NPCs as quest-givers:
- Track active and completed quests
- Provide quest objectives
- Give rewards
- React to quest completion

### Relationship System
NPCs remember interactions:
- Reputation tracking
- Trust levels
- Relationship types
- Influence dialogue and behavior

## Event Sourcing

All NPC interactions are recorded as events:

**Event Types:**
- `npc_interaction` - General interaction
- `npc_dialogue` - Dialogue exchange
- `npc_trade` - Trading activity
- `npc_combat` - Combat action
- `npc_relationship_update` - Relationship change
- `npc_spawn` - NPC spawned
- `npc_despawn` - NPC removed
- `npc_move` - NPC moved
- `npc_state_change` - State modified

This provides complete history of all NPC activities.

## Best Practices

1. **ID Convention** - Use `npc-` prefix for all NPC IDs
2. **Type Selection** - Choose appropriate NPC type for behavior
3. **Dialogue Variety** - Provide multiple dialogue options
4. **AI Configuration** - Match AI type to NPC role
5. **Relationship Tracking** - Use relationships for dynamic interactions
6. **Loot Balance** - Balance loot drops for game economy
7. **Schedule Realism** - Make schedules realistic for NPC type
8. **Customization** - Add distinctive features for memorable NPCs

## Performance Tips

- Use filtering when listing many NPCs
- Cache frequently accessed NPCs
- Use instancing for spawned enemies
- Clean up despawned NPCs
- Index NPCs by location for fast queries

## Future Enhancements

Potential additions:
- NPC factions and faction reputation
- Dynamic quest generation from NPCs
- NPC-to-NPC interactions
- NPC emotional states
- NPC memory of past interactions
- Group AI for coordinated NPC behavior
- Procedural NPC generation
- NPC leveling and progression

## See Also

- [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md) - Enhanced character features
- [API_README.md](API_README.md) - Core API documentation
- Character schemas in `bastards-blood/schemas/`

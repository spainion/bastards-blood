# Enhanced RPG Features Guide

This document describes the extended features added to the Bastards Blood RPG API, making it easily extensible for any RPG system with comprehensive inventory, equipment, crafting, skills, and customization support.

## Overview

The enhanced API now supports:
- 📦 **Advanced Inventory System** - Detailed items with properties, rarity, weight, value
- ⚔️ **Equipment & Slots** - 15+ equipment slots with custom slot support
- 🔨 **Crafting System** - Recipes, materials, professions, skill levels
- 📊 **Enhanced Stats & Attributes** - Core stats plus derived attributes
- 💫 **Status Effects** - Buffs, debuffs, durations, stacks
- 🎯 **Abilities & Skills** - Spells, special abilities, skill progression
- 💰 **Currency System** - Multiple currency types (gold, silver, copper)
- 🎨 **Character Customization** - Appearance, personality, traits
- 📈 **Experience & Leveling** - XP tracking, skill XP, profession levels

## Enhanced Character Schema

The system now supports an extended character schema at `schemas/character-extended.schema.json` with the following additions:

### Core Properties
```json
{
  "id": "char-hero",
  "name": "Brave Hero",
  "class": "Knight",
  "race": "Human",
  "lvl": 10,
  "xp": 15000
}
```

### Stats and Attributes
```json
{
  "stats": {
    "STR": 18,
    "DEX": 14,
    "CON": 16,
    "INT": 10,
    "WIS": 12,
    "CHA": 15
  },
  "attributes": {
    "speed": 30,
    "armor_class": 18,
    "initiative": 2,
    "carry_capacity": 180,
    "magic_resistance": 25
  }
}
```

### Resources
```json
{
  "hp": {
    "max": 100,
    "current": 85,
    "temp": 10
  },
  "resources": {
    "mana": {
      "max": 50,
      "current": 35
    },
    "stamina": {
      "max": 100,
      "current": 80
    }
  }
}
```

### Advanced Inventory
Items now have detailed properties:
```json
{
  "inventory": [
    {
      "id": "sword-of-flames",
      "name": "Sword of Flames",
      "type": "weapon",
      "quantity": 1,
      "weight": 3.5,
      "value": 500,
      "rarity": "rare",
      "properties": {
        "damage": "1d8+3",
        "damage_type": "fire",
        "enchantment": "+2",
        "special": "Burns on hit"
      }
    }
  ]
}
```

### Equipment Slots
Support for 15+ standard equipment slots plus custom slots:
```json
{
  "equipment": {
    "head": { "id": "helm-of-valor", "name": "Helm of Valor", "..." },
    "chest": { "id": "plate-armor", "name": "Plate Armor", "..." },
    "main_hand": { "id": "sword-of-flames", "name": "Sword of Flames", "..." },
    "off_hand": { "id": "tower-shield", "name": "Tower Shield", "..." },
    "ring_1": { "id": "ring-of-power", "name": "Ring of Power", "..." }
  }
}
```

**Standard Slots:**
- `head`, `neck`, `chest`, `back`, `hands`, `waist`, `legs`, `feet`
- `main_hand`, `off_hand`, `ranged`
- `ring_1`, `ring_2`, `trinket_1`, `trinket_2`
- Custom slots via `additionalProperties`

### Skills & Abilities
```json
{
  "skills": {
    "swordsmanship": {
      "level": 5,
      "xp": 1200,
      "bonus": 2
    },
    "lockpicking": {
      "level": 3,
      "xp": 450,
      "bonus": 1
    }
  },
  "abilities": [
    {
      "id": "fireball",
      "name": "Fireball",
      "type": "spell",
      "cost": {
        "mana": 15
      },
      "cooldown": 3,
      "description": "Launch a ball of fire"
    }
  ]
}
```

### Status Effects
```json
{
  "status_effects": [
    {
      "id": "blessing",
      "name": "Blessing",
      "type": "buff",
      "duration": 10,
      "stacks": 1,
      "effects": {
        "STR": 2,
        "WIS": 2
      }
    },
    {
      "id": "poison",
      "name": "Poisoned",
      "type": "debuff",
      "duration": 5,
      "stacks": 2,
      "effects": {
        "CON": -3
      }
    }
  ]
}
```

### Crafting System
```json
{
  "crafting": {
    "known_recipes": [
      "recipe-iron-sword",
      "recipe-health-potion",
      "recipe-leather-armor"
    ],
    "professions": {
      "blacksmithing": {
        "level": 5,
        "xp": 2400
      },
      "alchemy": {
        "level": 3,
        "xp": 800
      }
    }
  }
}
```

### Currency
```json
{
  "currency": {
    "gold": 1500,
    "silver": 250,
    "copper": 75,
    "gems": 5
  }
}
```

### Character Customization
```json
{
  "customization": {
    "appearance": {
      "height": "6'2\"",
      "weight": "190 lbs",
      "hair_color": "black",
      "eye_color": "blue",
      "skin_tone": "tan",
      "age": 28
    },
    "personality": {
      "alignment": "lawful good",
      "trait": "brave",
      "ideal": "justice",
      "bond": "protect the innocent",
      "flaw": "stubborn"
    }
  }
}
```

## API Endpoints

All extended endpoints are under `/api/v1/extended/` and require API key authentication.

### Get Extended Character
```bash
GET /api/v1/extended/characters/{character_id}
```

Returns full character data with all extended properties.

### Equip Item
```bash
POST /api/v1/extended/equip-item?session_id={session_id}
Content-Type: application/json

{
  "character_id": "char-hero",
  "item_id": "sword-of-flames",
  "slot": "main_hand"
}
```

### Unequip Item
```bash
POST /api/v1/extended/unequip-item?session_id={session_id}
Content-Type: application/json

{
  "character_id": "char-hero",
  "slot": "main_hand"
}
```

### Craft Item
```bash
POST /api/v1/extended/craft-item?session_id={session_id}
Content-Type: application/json

{
  "character_id": "char-hero",
  "recipe_id": "recipe-iron-sword",
  "quantity": 1
}
```

### Use Item
```bash
POST /api/v1/extended/use-item?session_id={session_id}
Content-Type: application/json

{
  "character_id": "char-hero",
  "item_id": "health-potion",
  "target_id": "char-hero"
}
```

### Trade Item
```bash
POST /api/v1/extended/trade-item?session_id={session_id}
Content-Type: application/json

{
  "from_character_id": "char-hero",
  "to_character_id": "char-mage",
  "item_id": "health-potion",
  "quantity": 2
}
```

### Apply Status Effect
```bash
POST /api/v1/extended/apply-status-effect?session_id={session_id}
Content-Type: application/json

{
  "character_id": "char-hero",
  "effect": {
    "id": "blessing",
    "name": "Blessing",
    "type": "buff",
    "duration": 10,
    "stacks": 1,
    "effects": {
      "STR": 2,
      "WIS": 2
    }
  }
}
```

### Learn Ability
```bash
POST /api/v1/extended/learn-ability?session_id={session_id}
Content-Type: application/json

{
  "character_id": "char-hero",
  "ability": {
    "id": "power-strike",
    "name": "Power Strike",
    "type": "ability",
    "cost": {
      "stamina": 10
    },
    "cooldown": 2,
    "description": "A powerful melee attack"
  }
}
```

### Learn Recipe
```bash
POST /api/v1/extended/learn-recipe?session_id={session_id}
Content-Type: application/json

{
  "character_id": "char-hero",
  "recipe_id": "recipe-iron-sword"
}
```

### Modify Attribute
```bash
POST /api/v1/extended/modify-attribute?session_id={session_id}
Content-Type: application/json

{
  "character_id": "char-hero",
  "attribute": "armor_class",
  "value": 20,
  "operation": "set"
}
```

Operations: `set`, `add`, `multiply`

## Event Types

The system now supports 18 additional event types:

- `equip_item` - Equip an item
- `unequip_item` - Unequip an item
- `craft_item` - Craft an item
- `use_item` - Use a consumable
- `trade_item` - Trade items
- `apply_status_effect` - Apply buff/debuff
- `remove_status_effect` - Remove effect
- `learn_ability` - Learn new ability
- `use_ability` - Use ability/spell
- `learn_recipe` - Learn crafting recipe
- `gain_xp` - Gain experience
- `level_up` - Level up character
- `modify_stat` - Modify base stat
- `modify_attribute` - Modify derived attribute
- `modify_resource` - Modify resource (mana, stamina)

## Extensibility

### Adding Custom Item Types
Simply extend the `ItemType` enum:
```python
class ItemType(str, Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    # ... existing types
    MOUNT = "mount"  # Add custom type
    PET = "pet"      # Add another
```

### Adding Custom Equipment Slots
The schema supports `additionalProperties` for equipment slots. Just add to your character data:
```json
{
  "equipment": {
    "pet_slot": { "id": "dragon-familiar", "name": "Dragon Familiar", "..." },
    "mount_slot": { "id": "war-horse", "name": "War Horse", "..." }
  }
}
```

### Adding Custom Attributes
The `attributes` field accepts any key-value pairs:
```json
{
  "attributes": {
    "custom_stat": 50,
    "spell_power": 100,
    "crit_chance": 25
  }
}
```

### Adding Custom Resources
Add any resource type to the `resources` object:
```json
{
  "resources": {
    "mana": { "max": 100, "current": 80 },
    "focus": { "max": 50, "current": 45 },
    "rage": { "max": 100, "current": 0 }
  }
}
```

### Adding Custom Currencies
The currency system is completely extensible:
```json
{
  "currency": {
    "gold": 1000,
    "platinum": 5,
    "faction_tokens": 250,
    "honor_points": 500
  }
}
```

## Example: Complete Enhanced Character

```json
{
  "id": "char-warrior",
  "name": "Ragnar the Bold",
  "class": "Berserker",
  "race": "Northman",
  "lvl": 15,
  "xp": 45000,
  "stats": {
    "STR": 20,
    "DEX": 14,
    "CON": 18,
    "INT": 8,
    "WIS": 10,
    "CHA": 12
  },
  "attributes": {
    "speed": 30,
    "armor_class": 16,
    "initiative": 2,
    "carry_capacity": 200,
    "damage_bonus": 5
  },
  "hp": {
    "max": 150,
    "current": 120,
    "temp": 15
  },
  "resources": {
    "stamina": {
      "max": 120,
      "current": 90
    },
    "rage": {
      "max": 100,
      "current": 45
    }
  },
  "inventory": [
    {
      "id": "great-axe",
      "name": "Great Axe of the North",
      "type": "weapon",
      "quantity": 1,
      "weight": 7.0,
      "value": 800,
      "rarity": "epic",
      "properties": {
        "damage": "2d6+5",
        "crit_range": "19-20",
        "special": "Cleave"
      }
    },
    {
      "id": "health-potion",
      "name": "Greater Health Potion",
      "type": "consumable",
      "quantity": 5,
      "weight": 0.5,
      "value": 50,
      "rarity": "common",
      "properties": {
        "healing": "4d8+10"
      }
    }
  ],
  "equipment": {
    "head": {
      "id": "helm-of-fury",
      "name": "Helm of Fury",
      "type": "armor",
      "rarity": "rare",
      "properties": {
        "armor_bonus": 2,
        "STR_bonus": 1
      }
    },
    "chest": {
      "id": "bearskin-armor",
      "name": "Bearskin Armor",
      "type": "armor",
      "rarity": "uncommon",
      "properties": {
        "armor_bonus": 5,
        "cold_resistance": 10
      }
    },
    "main_hand": {
      "id": "great-axe",
      "name": "Great Axe of the North",
      "type": "weapon",
      "rarity": "epic"
    }
  },
  "skills": {
    "axe_mastery": {
      "level": 7,
      "xp": 3500,
      "bonus": 3
    },
    "intimidation": {
      "level": 5,
      "xp": 2000,
      "bonus": 2
    }
  },
  "abilities": [
    {
      "id": "berserker-rage",
      "name": "Berserker Rage",
      "type": "ability",
      "cost": {
        "stamina": 20
      },
      "cooldown": 5,
      "description": "Enter a rage, gaining +5 STR and +3 damage for 10 rounds"
    },
    {
      "id": "whirlwind",
      "name": "Whirlwind Attack",
      "type": "ability",
      "cost": {
        "stamina": 30,
        "rage": 20
      },
      "cooldown": 3,
      "description": "Attack all enemies within reach"
    }
  ],
  "status_effects": [
    {
      "id": "battle-fury",
      "name": "Battle Fury",
      "type": "buff",
      "duration": 8,
      "stacks": 1,
      "effects": {
        "STR": 3,
        "damage_bonus": 2
      }
    }
  ],
  "currency": {
    "gold": 2500,
    "silver": 150
  },
  "customization": {
    "appearance": {
      "height": "6'4\"",
      "weight": "220 lbs",
      "hair_color": "red",
      "eye_color": "green",
      "skin_tone": "fair",
      "age": 32
    },
    "personality": {
      "alignment": "chaotic neutral",
      "trait": "fearless",
      "ideal": "glory in battle",
      "bond": "clan honor",
      "flaw": "reckless"
    }
  }
}
```

## RPG System Adaptability

This enhanced system can be easily adapted for various RPG systems:

### D&D 5e
- Use standard 6 stats (STR, DEX, CON, INT, WIS, CHA)
- Add proficiency bonus as attribute
- Equipment slots match D&D slots
- Spell slots as resources
- Add spell preparation system

### Pathfinder
- Similar to D&D with additional complexity
- Add feat system to abilities
- Skill ranks in skills
- Additional attributes for touch AC, flat-footed AC

### World of Darkness
- Replace stats with Attributes (Physical, Social, Mental)
- Add Skills system
- Willpower as resource
- Blood pool for vampires

### Cyberpunk
- Modern stats (BODY, REFLEX, TECH, etc.)
- Cyberware in equipment slots
- Humanity as resource
- Skills for technical abilities

### Custom Systems
The schema is fully extensible:
- Add any custom stats in `stats`
- Add any custom attributes in `attributes`
- Add any custom resources in `resources`
- Add any custom currencies in `currency`
- Add custom item types and properties
- Add custom equipment slots

## Best Practices

1. **Start Simple** - Use basic character schema, add extended features as needed
2. **Custom Properties** - Use `properties` field in items for game-specific data
3. **Event Sourcing** - All changes are events, enabling full history and rollback
4. **Validation** - Use JSON schemas to validate data integrity
5. **Extensibility** - Use `additionalProperties: true` for maximum flexibility

## Migration Guide

To migrate existing characters to extended format:

1. Add empty `equipment: {}` field
2. Convert simple inventory items to detailed item objects
3. Add optional fields as needed (resources, skills, abilities)
4. Keep existing data compatible - extended fields are all optional

Example migration:
```python
# Old format
old_char = {
    "id": "char-1",
    "inventory": ["sword", "shield"]
}

# New format
new_char = {
    "id": "char-1",
    "inventory": [
        {"id": "sword", "name": "Sword", "type": "weapon", "quantity": 1},
        {"id": "shield", "name": "Shield", "type": "armor", "quantity": 1}
    ],
    "equipment": {},
    "skills": {},
    "abilities": []
}
```

## Performance Considerations

- Event sourcing provides complete history but requires state reduction
- For large sessions, consider caching reduced state
- Pagination recommended for large inventories
- Index commonly queried fields (character_id, item_id, etc.)

## Future Enhancements

Potential additions:
- Quest system with objectives and rewards
- Faction reputation system
- Achievement/trophy tracking
- Character relationships and social networks
- Dynamic world events
- Weather and environmental effects
- Time management and calendar system

## Support

For questions or suggestions about the enhanced features, see the main API documentation or open an issue on the repository.

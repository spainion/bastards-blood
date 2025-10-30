# Bastards Blood RPG

A comprehensive AI-driven RPG system with FastAPI-based endpoint for managing game state, player actions, real-time gameplay, combat, and speech in a connected world. Features user accounts, database persistence, WebSocket support, combat system, event sourcing, and LLM integration.

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Start the API server
python run_server.py
```

Then visit http://localhost:8000/docs for interactive API documentation.

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[API_README.md](API_README.md)** - Complete API documentation
- **[ENHANCED_FEATURES.md](ENHANCED_FEATURES.md)** - Enhanced inventory, equipment, crafting, skills guide
- **[NPC_GUIDE.md](NPC_GUIDE.md)** - Complete NPC management system guide
- **[WORLD_GUIDE.md](WORLD_GUIDE.md)** - World coordinates, movement, actions, skills guide
- **[SKILLS_GUIDE.md](SKILLS_GUIDE.md)** - RuneScape-style progressive skills system
- **[REALTIME_COMBAT_GUIDE.md](REALTIME_COMBAT_GUIDE.md)** - 🆕 User accounts, real-time gameplay, combat, enemies guide
- **[examples/](examples/)** - Example usage scripts
- **[bastards-blood/](bastards-blood/)** - Data schemas and structure

## ✨ Features

### Core Features
- 🎮 **FastAPI Endpoint System** - RESTful API for RPG management (51 endpoints)
- 🔐 **Secure Authentication** - API key + JWT token-based access control
- 👥 **User Accounts** - Registration, login, user management with database persistence
- 📊 **Event Sourcing** - Complete game history with state reduction (56 event types)
- 🎲 **Player Actions** - Attacks, checks, healing, items, and more
- 💬 **Speech System** - Record and process player dialogue
- 🌍 **Multi-Campaign Support** - Manage multiple game worlds
- 🤖 **LLM-Ready** - Designed for AI integration
- 📝 **Auto-Generated Docs** - Interactive Swagger UI and ReDoc

### Database & Persistence
- 🗄️ **SQLAlchemy ORM** - Flexible database support (SQLite, PostgreSQL, MySQL)
- 💾 **Persistent Storage** - Characters, enemies, sessions, combat logs
- 🔄 **Auto-migrations** - Database schema auto-created on startup
- 📈 **User-Character Linking** - Characters belong to user accounts

### Real-time & Multiplayer
- ⚡ **WebSocket Support** - Real-time gameplay updates
- 👫 **Multiplayer** - See other players in real-time
- 💬 **Real-time Chat** - In-game chat system
- 🔔 **Live Notifications** - Combat updates, player movement, NPC interactions

### Combat System
- ⚔️ **Advanced Combat** - Damage calculation with crits, misses, armor mitigation
- 🎯 **Skill Integration** - Combat skills affect damage and defense
- 🏆 **XP & Rewards** - Gain XP and loot from defeating enemies
- 📜 **Combat Logs** - Complete combat history tracking
- 💥 **Damage Types** - Physical, fire, ice, lightning, poison, holy, dark, arcane

### Enemies & Mobs
- 👹 **10 Enemy Templates** - Goblins, orcs, trolls, dragons, demons, and more
- 📊 **Level Scaling** - Stats and rewards scale with enemy level
- 🤖 **AI Behaviors** - Aggressive, passive, patrol, flee, call for help
- 💰 **Loot System** - Random drops with customizable loot tables
- ♻️ **Respawn System** - Automatic enemy respawning
- 🗺️ **Spawn Management** - Create enemies at specific locations

### Enhanced Features
- 📦 **Advanced Inventory** - Detailed items with rarity, weight, value, custom properties
- ⚔️ **Equipment System** - 15+ equipment slots with custom slot support
- 🔨 **Crafting System** - Recipes, materials, professions, skill progression
- 📊 **Enhanced Stats** - Core stats plus unlimited derived attributes
- 💫 **Status Effects** - Buffs, debuffs with duration and stacking
- 🎯 **Abilities & Skills** - Spells, special abilities, skill leveling
- 💰 **Currency System** - Multiple currency types fully extensible
- 🎨 **Customization** - Character appearance, personality, traits
- 📈 **Progression** - XP tracking, leveling, profession advancement

### NPC Management System
- 🧙 **13 NPC Types** - Merchants, enemies, allies, quest-givers, bosses, companions, etc.
- 🤖 **Advanced AI** - Tactical, support, ranged, melee, caster AI types
- 💬 **Dynamic Dialogue** - Context-aware conversations with multiple categories
- 🛒 **Trading System** - Buy/sell with price modifiers and preferred items
- 📜 **Quest System** - NPCs give, track, and complete quests
- ❤️ **Relationships** - Reputation, trust, and relationship tracking
- 📅 **Schedules** - Daily routines and locations
- ⚔️ **Combat AI** - Intelligent combat behavior and target prioritization
- 🎲 **Loot Tables** - Customizable drops with currency and items
- 🎭 **Full Customization** - Appearance, voice, behavior patterns

### 🆕 World & Movement System
- 🗺️ **3D Coordinates** - X, Y, Z positioning with regions and areas
- 🏃 **10 Movement Types** - Walk, run, sprint, sneak, swim, fly, climb, and more
- ⚡ **Movement Mechanics** - Auto-calculated distance, duration, stamina costs
- 🎲 **D20 Skill System** - Skill checks with advantage/disadvantage, critical success/fail
- 📈 **Skill Progression** - XP-based skill leveling with automatic progression
- 🎯 **Action System** - 20+ action types (interact, examine, search, lock, unlock, etc.)
- 📍 **Location Tracking** - Complete location data with terrain and landmarks
- 🧭 **Spatial Queries** - Distance calculations, nearby entity detection
- 🚪 **Interactions** - Object interactions with skill check requirements
- 🗺️ **Pathfinding** - Automatic path calculation (planned feature)

### 🆕 RuneScape-Style Skills System
- 📊 **Progressive Leveling** - 120 level cap with exponential XP requirements
- 🎮 **24 Skills** - Combat, gathering, artisan, crafting, magic, and support skills
- 🏆 **Tier System** - Bronze → Iron → Steel → Mithril → Adamant → Rune → Dragon
- 💪 **Impact on Gameplay** - Higher levels improve success rates, unlock content
- 🎲 **Skill Checks** - Progressive checks where level affects success (5-95% range)
- 📈 **Automatic Leveling** - XP-based progression with automatic level-ups
- 🎯 **Skill Actions** - Mining, woodcutting, fishing, smithing, and more
- 🔓 **Content Unlocking** - Access to new equipment, resources, and areas by level
- 🧮 **Combat Level** - Calculated from combat skills
- 📊 **Total Level** - Sum of all skill levels for overall progression

**See [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md), [NPC_GUIDE.md](NPC_GUIDE.md), [WORLD_GUIDE.md](WORLD_GUIDE.md), and [SKILLS_GUIDE.md](SKILLS_GUIDE.md) for complete details.**

## 🎯 Use Cases

- Text-based RPG games with full spatial awareness
- AI-driven dungeon masters with movement and exploration
- Multi-player campaign management
- Discord/Slack bot backends
- LLM-powered narrative games with interactive worlds
- Game session recording and replay

## 🏗️ Architecture

The system uses **event sourcing** to maintain game state:
- All actions are recorded as events in an append-only log
- Current state is computed by reducing all events
- Enables complete history, replay, and time travel features

## 📖 API Overview

### Core Endpoints

- `GET /api/v1/characters` - List/manage characters
- `GET /api/v1/sessions` - List/manage game sessions
- `POST /api/v1/actions` - Perform player actions
- `POST /api/v1/speech` - Record player speech
- `GET /api/v1/sessions/{id}/state` - Get current game state

### Authentication

All endpoints require an API key via `X-API-Key` header:
```bash
curl -H "X-API-Key: your-secret-key" http://localhost:8000/api/v1/characters
```

## 🛠️ Development

Built with:
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **JSON Schema** - Schema validation
- **Event Sourcing** - State management pattern

## 📄 License

See repository license for details.

# Bastards Blood RPG API

A powerful FastAPI-based endpoint system for managing RPG game state, player actions, and speech within a complex game world. This API supports multiple RPG types, themes, and timelines with adaptive schema management and is designed for integration with LLM models.

## Features

- 🎮 **Adaptive RPG Schema Management** - Flexible JSON schema system for various RPG types
- 🔐 **Secure Authentication** - API key-based authentication for all endpoints
- 🎲 **Player Actions** - Handle attacks, checks, item management, and custom actions
- 💬 **Speech System** - Record and process player dialogue and NPC interactions
- 📊 **Event Sourcing** - Append-only event log with state reduction
- 🌍 **Multi-Campaign Support** - Manage multiple game campaigns simultaneously
- 🤖 **LLM-Ready** - Structured for integration with AI language models
- 📝 **Auto-Generated Docs** - Interactive API documentation via Swagger UI and ReDoc

## Installation

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and set your API_SECRET_KEY
   ```

3. **Run the Server**
   ```bash
   python run_server.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Documentation

Once the server is running, access the interactive documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

All API endpoints (except `/` and `/health`) require authentication via API key.

**Header Required:**
```
X-API-Key: your-secret-key-here
```

Set your API key in the `.env` file:
```
API_SECRET_KEY=your-secret-key-here
```

## Quick Start Examples

### 1. Check API Health
```bash
curl http://localhost:8000/health
```

### 2. Create a New Session
```bash
curl -X POST "http://localhost:8000/api/v1/sessions?session_id=2025-10-21-0001&campaign=my-campaign" \
  -H "X-API-Key: your-secret-key-here"
```

### 3. Create a Character
```bash
curl -X POST "http://localhost:8000/api/v1/characters" \
  -H "X-API-Key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "char-warrior",
    "name": "Warrior Bob",
    "class": "Warrior",
    "lvl": 5,
    "stats": {
      "STR": 18,
      "DEX": 12,
      "CON": 16,
      "INT": 10,
      "WIS": 11,
      "CHA": 8
    },
    "hp": {
      "max": 50,
      "current": 50
    },
    "inventory": ["sword", "shield"],
    "tags": ["party", "tank"]
  }'
```

### 4. Perform an Action
```bash
curl -X POST "http://localhost:8000/api/v1/actions" \
  -H "X-API-Key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "2025-10-21-0001",
    "actor_id": "char-warrior",
    "action_type": "attack",
    "target_id": "char-goblin",
    "data": {
      "weapon": "sword",
      "roll": 18
    }
  }'
```

### 5. Record Player Speech
```bash
curl -X POST "http://localhost:8000/api/v1/speech" \
  -H "X-API-Key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "2025-10-21-0001",
    "character_id": "char-warrior",
    "text": "I charge at the goblin with my sword!",
    "context": {
      "location": "dark_forest",
      "mood": "aggressive"
    }
  }'
```

### 6. Get Current Game State
```bash
curl "http://localhost:8000/api/v1/sessions/2025-10-21-0001/state" \
  -H "X-API-Key: your-secret-key-here"
```

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Health check

### Characters
- `GET /api/v1/characters` - List all characters
- `GET /api/v1/characters/{character_id}` - Get specific character
- `POST /api/v1/characters` - Create new character

### Sessions
- `GET /api/v1/sessions` - List all sessions
- `GET /api/v1/sessions/{session_id}` - Get specific session
- `POST /api/v1/sessions` - Create new session
- `GET /api/v1/sessions/{session_id}/state` - Get current game state

### Actions & Speech
- `POST /api/v1/actions` - Perform player action
- `POST /api/v1/speech` - Record player speech

## Event Types

The API supports the following event types for actions:

- `note` - General notes and observations
- `check` - Skill checks and ability tests
- `attack` - Combat attacks
- `damage` - Damage dealt to characters
- `heal` - Healing actions
- `gain_item` - Add items to inventory
- `lose_item` - Remove items from inventory
- `status` - Status effect changes
- `create_char` - Create new character in session
- `update_char` - Update character properties
- `custom` - Custom event types

## Architecture

### Event Sourcing
The API uses event sourcing to maintain game state:
1. All actions are recorded as events in an append-only log
2. Current game state is derived by "reducing" all events
3. This allows for:
   - Complete game history
   - Time travel and replay
   - Easy debugging and auditing
   - Undo/redo capabilities

### Data Structure
```
bastards-blood/
├── data/
│   ├── characters/    # Character JSON files
│   ├── sessions/      # Session event logs
│   └── campaigns/     # Campaign data (future)
└── schemas/           # JSON schemas for validation
    ├── character.schema.json
    ├── event.schema.json
    └── session.schema.json
```

## Configuration

Environment variables (set in `.env`):

```env
# API Configuration
API_SECRET_KEY=your-secret-key-here
API_TITLE=Bastards Blood RPG API
API_VERSION=1.0.0

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000"]

# Data paths
DATA_PATH=./bastards-blood/data
SCHEMAS_PATH=./bastards-blood/schemas

# LLM Configuration (optional)
LLM_API_KEY=your-llm-api-key
LLM_MODEL=gpt-4
LLM_ENDPOINT=https://api.openai.com/v1
```

## LLM Integration (Future Enhancement)

The API is designed to integrate with Large Language Models for:
- Dynamic NPC responses
- Narrative generation
- Context-aware game mastering
- Natural language action interpretation

The `speech` endpoint and event system provide the foundation for this integration.

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Structure
- `api/main.py` - FastAPI application and endpoints
- `api/models.py` - Pydantic models for validation
- `api/data_manager.py` - Data persistence and state management
- `api/auth.py` - Authentication system
- `api/config.py` - Configuration management

## Use Cases

This API is ideal for:
- Text-based RPG games
- AI-driven dungeon masters
- Multi-player campaign management
- RPG game state persistence
- Integration with chat interfaces (Discord, Slack, etc.)
- LLM-powered narrative games
- Game session recording and replay

## Contributing

Contributions are welcome! The system is designed to be extensible for:
- New event types
- Custom game mechanics
- Additional RPG systems
- Enhanced LLM integration

## License

See repository license for details.

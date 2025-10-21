# Bastards Blood RPG

A powerful AI-driven text RPG system with a FastAPI-based endpoint for managing game state, player actions, and speech in a connected world and environment. Features event sourcing, adaptive schema management, and LLM integration capabilities.

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
python run_server.py
```

Then visit http://localhost:8000/docs for interactive API documentation.

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[API_README.md](API_README.md)** - Complete API documentation
- **[examples/](examples/)** - Example usage scripts
- **[bastards-blood/](bastards-blood/)** - Data schemas and structure

## ✨ Features

- 🎮 **FastAPI Endpoint System** - RESTful API for RPG management
- 🔐 **Secure Authentication** - API key-based access control
- 📊 **Event Sourcing** - Complete game history with state reduction
- 🎲 **Player Actions** - Attacks, checks, healing, items, and more
- 💬 **Speech System** - Record and process player dialogue
- 🌍 **Multi-Campaign Support** - Manage multiple game worlds
- 🤖 **LLM-Ready** - Designed for AI integration
- 📝 **Auto-Generated Docs** - Interactive Swagger UI and ReDoc

## 🎯 Use Cases

- Text-based RPG games
- AI-driven dungeon masters
- Multi-player campaign management
- Discord/Slack bot backends
- LLM-powered narrative games
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

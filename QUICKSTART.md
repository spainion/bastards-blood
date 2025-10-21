# Quick Start Guide

Get the Bastards Blood RPG API up and running in 5 minutes!

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and change API_SECRET_KEY to a secure value
```

**Important:** Change the default API key in production!

## 3. Start the Server

```bash
python run_server.py
```

The server will start on `http://localhost:8000`

## 4. View API Documentation

Open your browser to:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 5. Test the API

### Using curl:

```bash
# Health check (no auth required)
curl http://localhost:8000/health

# List characters (requires API key)
curl -H "X-API-Key: dev-secret-key-change-in-production" \
  http://localhost:8000/api/v1/characters
```

### Using the example script:

```bash
python examples/basic_usage.py
```

## What's Next?

- Read the full [API Documentation](API_README.md)
- Explore the [examples](examples/) directory
- Check out the [Swagger UI](http://localhost:8000/docs) for interactive testing
- Review the existing [JSON schemas](bastards-blood/schemas/)

## Key Concepts

### Authentication
All endpoints (except `/` and `/health`) require an API key via the `X-API-Key` header.

### Event Sourcing
The API uses event sourcing to track game state:
- All actions are stored as events
- Current state is computed by "reducing" events
- Complete game history is preserved

### Sessions
A session is a container for a game campaign with an event log. Create a session before performing actions.

### Characters
Characters can be created globally and then added to sessions via events.

## Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
- **Solution:** Run `pip install -r requirements.txt`

**Problem:** `Missing API key` error
- **Solution:** Add the `X-API-Key` header to your requests

**Problem:** Server won't start on port 8000
- **Solution:** Change the `PORT` in `.env` or use: `PORT=8080 python run_server.py`

**Problem:** Character not found in session
- **Solution:** Characters must be added to a session via a `create_char` event before they can perform actions

## Support

For more information, see:
- [API_README.md](API_README.md) - Full API documentation
- [examples/](examples/) - Example usage scripts
- [bastards-blood/README.md](bastards-blood/README.md) - Data structure documentation

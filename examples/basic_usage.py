#!/usr/bin/env python3
"""
Example script demonstrating basic usage of the Bastards Blood RPG API.
This shows how to interact with the API programmatically.
"""
import requests
import json

# API Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "dev-secret-key-change-in-production"  # Change in production!
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}


def check_health():
    """Check if the API is healthy."""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", json.dumps(response.json(), indent=2))
    return response.json()


def create_session(session_id, campaign="demo-campaign"):
    """Create a new game session."""
    response = requests.post(
        f"{BASE_URL}/api/v1/sessions",
        headers=HEADERS,
        params={"session_id": session_id, "campaign": campaign}
    )
    print(f"\nCreated Session: {session_id}")
    print(json.dumps(response.json(), indent=2))
    return response.json()


def create_character(character_data):
    """Create a new character."""
    response = requests.post(
        f"{BASE_URL}/api/v1/characters",
        headers=HEADERS,
        json=character_data
    )
    print(f"\nCreated Character: {character_data['id']}")
    print(json.dumps(response.json(), indent=2))
    return response.json()


def perform_action(session_id, actor_id, action_type, target_id=None, data=None):
    """Perform a game action."""
    action_data = {
        "session_id": session_id,
        "actor_id": actor_id,
        "action_type": action_type,
        "target_id": target_id,
        "data": data or {}
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/actions",
        headers=HEADERS,
        json=action_data
    )
    print(f"\nPerformed Action: {action_type}")
    print(json.dumps(response.json(), indent=2))
    return response.json()


def record_speech(session_id, character_id, text, context=None):
    """Record character speech."""
    speech_data = {
        "session_id": session_id,
        "character_id": character_id,
        "text": text,
        "context": context or {}
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/speech",
        headers=HEADERS,
        json=speech_data
    )
    print(f"\nRecorded Speech from {character_id}:")
    print(json.dumps(response.json(), indent=2))
    return response.json()


def get_game_state(session_id):
    """Get current game state."""
    response = requests.get(
        f"{BASE_URL}/api/v1/sessions/{session_id}/state",
        headers=HEADERS
    )
    print(f"\nCurrent Game State:")
    print(json.dumps(response.json(), indent=2))
    return response.json()


def main():
    """Run example workflow."""
    print("=" * 60)
    print("Bastards Blood RPG API - Example Usage")
    print("=" * 60)
    
    # 1. Check API health
    check_health()
    
    # 2. Create a session
    session_id = "example-session-001"
    create_session(session_id, "example-campaign")
    
    # 3. Create a character
    hero = {
        "id": "char-hero",
        "name": "Brave Hero",
        "class": "Knight",
        "lvl": 3,
        "stats": {
            "STR": 16,
            "DEX": 12,
            "CON": 14,
            "INT": 10,
            "WIS": 13,
            "CHA": 15
        },
        "hp": {
            "max": 40,
            "current": 40
        },
        "inventory": ["sword", "shield", "potion"],
        "tags": ["hero", "party"]
    }
    create_character(hero)
    
    # 4. Add character to session (via create_char event)
    perform_action(
        session_id=session_id,
        actor_id="system",
        action_type="create_char",
        data={"character": hero}
    )
    
    # 5. Record speech
    record_speech(
        session_id=session_id,
        character_id="char-hero",
        text="I shall defeat the dragon and save the kingdom!",
        context={"location": "castle", "mood": "determined"}
    )
    
    # 6. Perform an attack
    perform_action(
        session_id=session_id,
        actor_id="char-hero",
        action_type="attack",
        target_id="char-dragon",
        data={"weapon": "sword", "roll": 19, "crit": True}
    )
    
    # 7. Take damage
    perform_action(
        session_id=session_id,
        actor_id="char-hero",
        action_type="damage",
        data={"id": "char-hero", "amount": 10}
    )
    
    # 8. Use a healing potion
    perform_action(
        session_id=session_id,
        actor_id="char-hero",
        action_type="heal",
        data={"id": "char-hero", "amount": 15}
    )
    
    # 9. Get final game state
    get_game_state(session_id)
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API. Make sure the server is running:")
        print("  python run_server.py")
    except Exception as e:
        print(f"\nError: {e}")

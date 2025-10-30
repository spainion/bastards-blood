"""Main FastAPI application for the RPG endpoint system."""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from typing import Dict, Any, List
import os
import logging

from .config import settings
from .auth import verify_api_key
from .models import (
    ActionRequest, ActionResponse, SpeechRequest,
    GameStateResponse, HealthCheckResponse, Character, Session
)
from .data_manager import data_manager

# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="""
    A powerful AI-driven RPG endpoint system for managing game state, player actions, 
    and speech within a complicated game world. Supports multiple RPG types, themes, 
    and timelines with adaptive schema management.
    
    ## Features
    - 🎮 Adaptive RPG schema management
    - 🔐 Secure API key authentication
    - 🎲 Player action and speech endpoints
    - 📊 Event sourcing and state management
    - 🌍 Multi-campaign support
    - 🤖 Ready for LLM integration
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logger = logging.getLogger(__name__)


@app.get("/", tags=["Health"])
async def root() -> Dict[str, str]:
    """Root endpoint - API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check() -> HealthCheckResponse:
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version=settings.api_version,
        timestamp=datetime.now(timezone.utc)
    )


@app.get("/api/v1/characters", tags=["Characters"], dependencies=[Depends(verify_api_key)])
async def list_characters() -> Dict[str, Any]:
    """List all available characters."""
    character_ids = data_manager.list_characters()
    characters = []
    
    for char_id in character_ids:
        char_data = data_manager.load_character(char_id)
        if char_data:
            characters.append(char_data)
    
    return {
        "characters": characters,
        "count": len(characters)
    }


@app.get("/api/v1/characters/{character_id}", tags=["Characters"], dependencies=[Depends(verify_api_key)])
async def get_character(character_id: str) -> Character:
    """Get a specific character by ID."""
    char_data = data_manager.load_character(character_id)
    if not char_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {character_id} not found"
        )
    return Character(**char_data)


@app.post("/api/v1/characters", tags=["Characters"], dependencies=[Depends(verify_api_key)])
async def create_character(character: Character) -> Dict[str, Any]:
    """Create a new character."""
    # Check if character already exists
    existing = data_manager.load_character(character.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Character {character.id} already exists"
        )
    
    # Save character
    char_dict = character.model_dump(by_alias=True)
    data_manager.save_character(char_dict)
    
    return {
        "success": True,
        "message": f"Character {character.id} created successfully",
        "character": char_dict
    }


@app.get("/api/v1/sessions", tags=["Sessions"], dependencies=[Depends(verify_api_key)])
async def list_sessions() -> Dict[str, Any]:
    """List all game sessions."""
    session_ids = data_manager.list_sessions()
    return {
        "sessions": session_ids,
        "count": len(session_ids)
    }


@app.get("/api/v1/sessions/{session_id}", tags=["Sessions"], dependencies=[Depends(verify_api_key)])
async def get_session(session_id: str) -> Session:
    """Get a specific session by ID."""
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    return Session(**session_data)


@app.post("/api/v1/sessions", tags=["Sessions"], dependencies=[Depends(verify_api_key)])
async def create_session(session_id: str, campaign: str = "bastards-blood") -> Dict[str, Any]:
    """Create a new game session."""
    # Check if session already exists
    existing = data_manager.load_session(session_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Session {session_id} already exists"
        )
    
    session = data_manager.create_session(session_id, campaign)
    return {
        "success": True,
        "message": f"Session {session_id} created successfully",
        "session": session
    }


@app.get("/api/v1/sessions/{session_id}/state", response_model=GameStateResponse, tags=["Sessions"], dependencies=[Depends(verify_api_key)])
async def get_game_state(session_id: str) -> GameStateResponse:
    """Get the current game state for a session by reducing all events."""
    session_data = data_manager.load_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    state = data_manager.reduce_state(session_id)
    
    # Convert characters dict to Character models
    characters = {}
    for char_id, char_data in state.get("characters", {}).items():
        try:
            characters[char_id] = Character(**char_data)
        except Exception as e:
            # If character data is invalid, skip it
            logger.warning(f"Invalid character data for {char_id}: {e}")
    
    return GameStateResponse(
        characters=characters,
        session_id=session_id,
        campaign=session_data.get("campaign", "unknown"),
        event_count=len(session_data.get("events", []))
    )


@app.post("/api/v1/actions", response_model=ActionResponse, tags=["Actions"], dependencies=[Depends(verify_api_key)])
async def perform_action(action: ActionRequest) -> ActionResponse:
    """
    Perform a player action in the game.
    
    This endpoint handles various RPG actions like attacks, skill checks, item usage, etc.
    The action is recorded as an event in the session's event log.
    """
    # Verify session exists
    session_data = data_manager.load_session(action.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {action.session_id} not found"
        )
    
    # Verify actor exists in current state
    state = data_manager.reduce_state(action.session_id)
    if action.actor_id not in state.get("characters", {}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {action.actor_id} not found in session"
        )
    
    # Create event
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": action.action_type.value,
        "actor": action.actor_id,
        "target": action.target_id,
        "data": action.data,
        "result": {}
    }
    
    # Add event to session
    data_manager.add_event_to_session(action.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message=f"Action {action.action_type.value} performed successfully",
        result=event.get("result", {})
    )


@app.post("/api/v1/speech", response_model=ActionResponse, tags=["Speech"], dependencies=[Depends(verify_api_key)])
async def handle_speech(speech: SpeechRequest) -> ActionResponse:
    """
    Handle player speech/dialogue in the game.
    
    This endpoint records player speech as a note event and can be used to trigger
    NPC responses or other game events through LLM integration.
    """
    # Verify session exists
    session_data = data_manager.load_session(speech.session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {speech.session_id} not found"
        )
    
    # Verify character exists in current state
    state = data_manager.reduce_state(speech.session_id)
    if speech.character_id not in state.get("characters", {}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character {speech.character_id} not found in session"
        )
    
    # Create speech event as a note
    event_id = data_manager.generate_event_id()
    event = {
        "id": event_id,
        "ts": datetime.now(timezone.utc).isoformat() + 'Z',
        "t": "note",
        "actor": speech.character_id,
        "data": {
            "text": speech.text,
            "type": "speech",
            "context": speech.context
        },
        "result": {}
    }
    
    # Add event to session
    data_manager.add_event_to_session(speech.session_id, event)
    
    return ActionResponse(
        success=True,
        event_id=event_id,
        message="Speech recorded successfully",
        result={"text": speech.text}
    )


# Include extended features router
try:
    from .endpoints_extended import router as extended_router
    app.include_router(extended_router)
except ImportError:
    logger.warning("Extended endpoints not available")

# Include NPC router
try:
    from .endpoints_npc import router as npc_router
    app.include_router(npc_router)
except ImportError:
    logger.warning("NPC endpoints not available")


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )

"""Quest system endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid
import logging

from .auth import verify_api_key
from .models_quest import (
    Quest, QuestProgress, QuestStartRequest, QuestUpdateRequest,
    QuestCompleteRequest, QuestAbandonRequest, QuestResponse,
    QuestStatus, QuestLine
)
from .data_manager import data_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/quests", tags=["Quests"])


# In-memory quest storage (should be moved to database in production)
QUEST_TEMPLATES: Dict[str, Quest] = {}
CHARACTER_QUEST_PROGRESS: Dict[str, QuestProgress] = {}


def _get_quest_progress(character_id: str) -> QuestProgress:
    """Get or create quest progress for a character."""
    if character_id not in CHARACTER_QUEST_PROGRESS:
        CHARACTER_QUEST_PROGRESS[character_id] = QuestProgress(character_id=character_id)
    return CHARACTER_QUEST_PROGRESS[character_id]


def _check_prerequisites(character_id: str, quest: Quest) -> bool:
    """Check if character meets quest prerequisites."""
    progress = _get_quest_progress(character_id)
    
    # Check if all prerequisite quests are completed
    for prereq_id in quest.prerequisites:
        if prereq_id not in progress.completed_quests:
            return False
    
    return True


def _update_objectives(quest: Quest, objective_id: str, progress_amount: int) -> bool:
    """Update quest objective progress."""
    for objective in quest.objectives:
        if objective.id == objective_id:
            objective.current = min(objective.current + progress_amount, objective.required)
            if objective.current >= objective.required:
                objective.completed = True
            return True
    return False


def _check_completion(quest: Quest) -> bool:
    """Check if all required objectives are completed."""
    return all(obj.completed or obj.optional for obj in quest.objectives)


@router.post("/start", response_model=QuestResponse, dependencies=[Depends(verify_api_key)])
async def start_quest(request: QuestStartRequest) -> QuestResponse:
    """Start a quest for a character."""
    try:
        # Get quest template
        if request.quest_id not in QUEST_TEMPLATES:
            raise HTTPException(status_code=404, detail=f"Quest {request.quest_id} not found")
        
        quest_template = QUEST_TEMPLATES[request.quest_id]
        progress = _get_quest_progress(request.character_id)
        
        # Check if already active
        if request.quest_id in progress.active_quests:
            raise HTTPException(status_code=400, detail="Quest already active")
        
        # Check if completed and not repeatable
        if request.quest_id in progress.completed_quests and not quest_template.repeatable:
            raise HTTPException(status_code=400, detail="Quest already completed and not repeatable")
        
        # Check prerequisites
        if not _check_prerequisites(request.character_id, quest_template):
            raise HTTPException(status_code=400, detail="Prerequisites not met")
        
        # Create quest instance
        quest = quest_template.model_copy()
        quest.status = QuestStatus.ACTIVE
        quest.started_at = datetime.now(timezone.utc)
        
        # Update progress
        progress.active_quests.append(request.quest_id)
        progress.quest_data[request.quest_id] = quest
        
        # Record event
        event_id = str(uuid.uuid4())
        data_manager.record_event(
            request.session_id,
            request.character_id,
            "quest_started",
            {"quest_id": request.quest_id, "quest_name": quest.name},
            event_id
        )
        
        return QuestResponse(
            success=True,
            message=f"Quest '{quest.name}' started",
            quest=quest,
            progress=progress,
            event_id=event_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting quest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update", response_model=QuestResponse, dependencies=[Depends(verify_api_key)])
async def update_quest_progress(request: QuestUpdateRequest) -> QuestResponse:
    """Update quest objective progress."""
    try:
        progress = _get_quest_progress(request.character_id)
        
        # Check if quest is active
        if request.quest_id not in progress.active_quests:
            raise HTTPException(status_code=400, detail="Quest not active")
        
        quest = progress.quest_data[request.quest_id]
        
        # Update objective
        if not _update_objectives(quest, request.objective_id, request.progress):
            raise HTTPException(status_code=404, detail="Objective not found")
        
        # Record event
        event_id = str(uuid.uuid4())
        data_manager.record_event(
            request.session_id,
            request.character_id,
            "quest_progress",
            {
                "quest_id": request.quest_id,
                "objective_id": request.objective_id,
                "progress": request.progress
            },
            event_id
        )
        
        return QuestResponse(
            success=True,
            message="Quest progress updated",
            quest=quest,
            progress=progress,
            event_id=event_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating quest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete", response_model=QuestResponse, dependencies=[Depends(verify_api_key)])
async def complete_quest(request: QuestCompleteRequest) -> QuestResponse:
    """Complete a quest and grant rewards."""
    try:
        progress = _get_quest_progress(request.character_id)
        
        # Check if quest is active
        if request.quest_id not in progress.active_quests:
            raise HTTPException(status_code=400, detail="Quest not active")
        
        quest = progress.quest_data[request.quest_id]
        
        # Check if all objectives are completed
        if not _check_completion(quest):
            raise HTTPException(status_code=400, detail="Not all objectives completed")
        
        # Update status
        quest.status = QuestStatus.COMPLETED
        quest.completed_at = datetime.now(timezone.utc)
        
        # Update progress
        progress.active_quests.remove(request.quest_id)
        progress.completed_quests.append(request.quest_id)
        
        # Grant rewards (simplified - should integrate with character/inventory system)
        rewards_granted = {
            "experience": quest.rewards.experience,
            "gold": quest.rewards.gold,
            "items": quest.rewards.items,
            "reputation": quest.rewards.reputation,
            "skills": quest.rewards.skills,
            "unlocks": quest.rewards.unlocks
        }
        
        # Record event
        event_id = str(uuid.uuid4())
        data_manager.record_event(
            request.session_id,
            request.character_id,
            "quest_completed",
            {
                "quest_id": request.quest_id,
                "quest_name": quest.name,
                "rewards": rewards_granted
            },
            event_id
        )
        
        return QuestResponse(
            success=True,
            message=f"Quest '{quest.name}' completed! Rewards granted.",
            quest=quest,
            progress=progress,
            event_id=event_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing quest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/abandon", response_model=QuestResponse, dependencies=[Depends(verify_api_key)])
async def abandon_quest(request: QuestAbandonRequest) -> QuestResponse:
    """Abandon an active quest."""
    try:
        progress = _get_quest_progress(request.character_id)
        
        # Check if quest is active
        if request.quest_id not in progress.active_quests:
            raise HTTPException(status_code=400, detail="Quest not active")
        
        quest = progress.quest_data[request.quest_id]
        quest.status = QuestStatus.ABANDONED
        
        # Update progress
        progress.active_quests.remove(request.quest_id)
        progress.failed_quests.append(request.quest_id)
        
        # Record event
        event_id = str(uuid.uuid4())
        data_manager.record_event(
            request.session_id,
            request.character_id,
            "quest_abandoned",
            {"quest_id": request.quest_id, "quest_name": quest.name},
            event_id
        )
        
        return QuestResponse(
            success=True,
            message=f"Quest '{quest.name}' abandoned",
            quest=quest,
            progress=progress,
            event_id=event_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error abandoning quest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/character/{character_id}", response_model=QuestProgress, dependencies=[Depends(verify_api_key)])
async def get_character_quests(character_id: str) -> QuestProgress:
    """Get quest progress for a character."""
    progress = _get_quest_progress(character_id)
    return progress


@router.get("/available/{character_id}", dependencies=[Depends(verify_api_key)])
async def get_available_quests(character_id: str) -> Dict[str, List[Quest]]:
    """Get available quests for a character."""
    progress = _get_quest_progress(character_id)
    available = []
    
    for quest_id, quest in QUEST_TEMPLATES.items():
        # Skip if already active or completed (and not repeatable)
        if quest_id in progress.active_quests:
            continue
        if quest_id in progress.completed_quests and not quest.repeatable:
            continue
        
        # Check prerequisites
        if _check_prerequisites(character_id, quest):
            available.append(quest)
    
    return {"available_quests": available, "count": len(available)}


@router.get("/template/{quest_id}", response_model=Quest, dependencies=[Depends(verify_api_key)])
async def get_quest_template(quest_id: str) -> Quest:
    """Get a quest template by ID."""
    if quest_id not in QUEST_TEMPLATES:
        raise HTTPException(status_code=404, detail="Quest not found")
    return QUEST_TEMPLATES[quest_id]


@router.get("/templates", dependencies=[Depends(verify_api_key)])
async def list_quest_templates() -> Dict[str, Any]:
    """List all quest templates."""
    return {
        "quests": list(QUEST_TEMPLATES.values()),
        "count": len(QUEST_TEMPLATES)
    }


@router.post("/template/create", response_model=Quest, dependencies=[Depends(verify_api_key)])
async def create_quest_template(quest: Quest) -> Quest:
    """Create a new quest template."""
    if quest.id in QUEST_TEMPLATES:
        raise HTTPException(status_code=400, detail="Quest ID already exists")
    
    QUEST_TEMPLATES[quest.id] = quest
    logger.info(f"Created quest template: {quest.id}")
    return quest


@router.delete("/template/{quest_id}", dependencies=[Depends(verify_api_key)])
async def delete_quest_template(quest_id: str) -> Dict[str, str]:
    """Delete a quest template."""
    if quest_id not in QUEST_TEMPLATES:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    del QUEST_TEMPLATES[quest_id]
    logger.info(f"Deleted quest template: {quest_id}")
    return {"message": f"Quest {quest_id} deleted"}


@router.get("/questlines/{character_id}", dependencies=[Depends(verify_api_key)])
async def get_questlines(character_id: str) -> Dict[str, Any]:
    """Get questline progress for a character."""
    progress = _get_quest_progress(character_id)
    return {
        "questlines": progress.questlines,
        "count": len(progress.questlines)
    }

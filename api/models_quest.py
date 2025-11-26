"""Pydantic models for quest system."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class QuestStatus(str, Enum):
    """Quest status enum."""
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class ObjectiveType(str, Enum):
    """Quest objective types."""
    KILL = "kill"
    COLLECT = "collect"
    TALK = "talk"
    EXPLORE = "explore"
    ESCORT = "escort"
    CRAFT = "craft"
    DELIVER = "deliver"
    DEFEND = "defend"
    CUSTOM = "custom"


class QuestObjective(BaseModel):
    """Quest objective model."""
    id: str = Field(..., description="Unique objective ID")
    type: ObjectiveType = Field(..., description="Type of objective")
    description: str = Field(..., description="Objective description")
    target: str = Field(..., description="Target entity/item/location")
    current: int = Field(default=0, description="Current progress")
    required: int = Field(..., description="Required amount")
    completed: bool = Field(default=False, description="Whether objective is completed")
    optional: bool = Field(default=False, description="Whether objective is optional")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Conditional requirements")


class QuestReward(BaseModel):
    """Quest reward model."""
    experience: int = Field(default=0, description="XP reward")
    gold: int = Field(default=0, description="Gold reward")
    items: List[Dict[str, Any]] = Field(default_factory=list, description="Item rewards")
    reputation: Dict[str, int] = Field(default_factory=dict, description="Reputation changes")
    skills: Dict[str, int] = Field(default_factory=dict, description="Skill XP rewards")
    unlocks: List[str] = Field(default_factory=list, description="Unlocked content IDs")


class Quest(BaseModel):
    """Quest model."""
    id: str = Field(..., description="Unique quest ID")
    name: str = Field(..., description="Quest name")
    description: str = Field(..., description="Quest description")
    level_requirement: int = Field(default=1, description="Minimum level requirement")
    prerequisites: List[str] = Field(default_factory=list, description="Required quest IDs")
    objectives: List[QuestObjective] = Field(..., description="Quest objectives")
    rewards: QuestReward = Field(..., description="Quest rewards")
    status: QuestStatus = Field(default=QuestStatus.NOT_STARTED, description="Quest status")
    category: str = Field(default="main", description="Quest category (main, side, daily, etc.)")
    repeatable: bool = Field(default=False, description="Whether quest is repeatable")
    time_limit: Optional[int] = Field(default=None, description="Time limit in seconds")
    started_at: Optional[datetime] = Field(default=None, description="When quest was started")
    completed_at: Optional[datetime] = Field(default=None, description="When quest was completed")
    story_branch: Optional[str] = Field(default=None, description="Story branch identifier")
    next_quests: List[str] = Field(default_factory=list, description="Unlocked quest IDs")


class QuestLine(BaseModel):
    """Quest line/chain model."""
    id: str = Field(..., description="Unique questline ID")
    name: str = Field(..., description="Questline name")
    description: str = Field(..., description="Questline description")
    quests: List[str] = Field(..., description="Quest IDs in order")
    current_quest: Optional[str] = Field(default=None, description="Current active quest ID")
    completed: bool = Field(default=False, description="Whether questline is completed")


class QuestProgress(BaseModel):
    """Character quest progress model."""
    character_id: str = Field(..., description="Character ID")
    active_quests: List[str] = Field(default_factory=list, description="Active quest IDs")
    completed_quests: List[str] = Field(default_factory=list, description="Completed quest IDs")
    failed_quests: List[str] = Field(default_factory=list, description="Failed quest IDs")
    quest_data: Dict[str, Quest] = Field(default_factory=dict, description="Quest state data")
    questlines: Dict[str, QuestLine] = Field(default_factory=dict, description="Questline progress")


class QuestStartRequest(BaseModel):
    """Request to start a quest."""
    character_id: str = Field(..., description="Character ID")
    quest_id: str = Field(..., description="Quest ID to start")
    session_id: str = Field(..., description="Session ID")


class QuestUpdateRequest(BaseModel):
    """Request to update quest progress."""
    character_id: str = Field(..., description="Character ID")
    quest_id: str = Field(..., description="Quest ID")
    objective_id: str = Field(..., description="Objective ID")
    progress: int = Field(..., description="Progress amount to add")
    session_id: str = Field(..., description="Session ID")


class QuestCompleteRequest(BaseModel):
    """Request to complete a quest."""
    character_id: str = Field(..., description="Character ID")
    quest_id: str = Field(..., description="Quest ID")
    session_id: str = Field(..., description="Session ID")


class QuestAbandonRequest(BaseModel):
    """Request to abandon a quest."""
    character_id: str = Field(..., description="Character ID")
    quest_id: str = Field(..., description="Quest ID")
    session_id: str = Field(..., description="Session ID")


class QuestResponse(BaseModel):
    """Quest response model."""
    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Response message")
    quest: Optional[Quest] = Field(default=None, description="Quest data")
    progress: Optional[QuestProgress] = Field(default=None, description="Quest progress data")
    event_id: Optional[str] = Field(default=None, description="Event ID for sourcing")

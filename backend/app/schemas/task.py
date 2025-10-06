from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

from app.schemas.user import UserBase
from app.schemas.tag import Tag
from app.schemas.history import History


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# --- Base Schema ---


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: Literal["todo", "in-progress", "done"] = "todo"
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


# --- Create Schema ---


class TaskCreate(TaskBase):
    assigned_user_ids: List[int] = []
    tag_ids: List[int] = []


# --- Update Schema ---


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_user_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None


# --- Read Schema ---


class Task(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    assigned_users: List[UserBase] = []
    tags: List[Tag] = []
    history: List[History] = []

    model_config = ConfigDict(from_attributes=True)

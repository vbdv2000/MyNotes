from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserBase

# --- Base Schema ---


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Literal["todo", "in-progress", "done"] = "todo"


# --- Create Schema ---


class TaskCreate(TaskBase):
    assigned_user_ids: List[int] = []


# --- Update Schema ---


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_user_ids: Optional[List[int]] = None


# --- Read Schema ---


class Task(TaskBase):
    id: int
    project_id: int
    assigned_users: List[UserBase] = []

    model_config = ConfigDict(from_attributes=True)

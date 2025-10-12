from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

# Importar esquemas
from app.schemas.task import Task
from app.schemas.user import UserBase
from app.schemas.tag import Tag
from app.schemas.history import History

# --- Base Schema ---


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


# --- Create Schema ---


class ProjectCreate(ProjectBase):
    owner_id: Optional[int] = None
    collaborator_ids: List[int] = []
    tag_ids: List[int] = []


# --- Update Schema ---


class ProjectUpdate(ProjectBase):
    title: Optional[str] = None
    description: Optional[str] = None
    collaborator_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None


# --- Read Schema ---


class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    owner: UserBase
    collaborators: List[UserBase] = []
    tasks: List[Task] = []
    tags: List[Tag] = []
    history: List[History] = []

    model_config = ConfigDict(from_attributes=True)

from typing import Optional, List
from pydantic import BaseModel, ConfigDict

# Importar esquemas
from app.schemas.task import Task
from app.schemas.user import UserBase 

# --- Base Schema ---

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    
# --- Create Schema ---

class ProjectCreate(ProjectBase):
    owner_id: int
    collaborator_ids: List[int] = []
    
# --- Update Schema ---

class ProjectUpdate(ProjectBase):
    title: Optional[str] = None
    description: Optional[str] = None
    collaborator_ids: Optional[List[int]] = None 

# --- Read Schema ---

class Project(ProjectBase):
    id: int
    owner_id: int
    owner: UserBase
    collaborators: List[UserBase] = []
    tasks: List[Task] = []
    
    model_config = ConfigDict(from_attributes=True)
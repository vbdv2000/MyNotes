from typing import Optional, List
from pydantic import BaseModel, ConfigDict

# --- Base Schema for Relationships ---

class UserBase(BaseModel):
    id: Optional[int] = None
    email: str
    full_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Create and Update Schemas ---

class UserCreate(UserBase):
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

class UserUpdate(UserBase):
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    
# --- Read Schema (Excludes Password) ---

class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

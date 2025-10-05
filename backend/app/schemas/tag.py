from pydantic import BaseModel, Field
from typing import Optional


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = "#808080"  # Default gray color


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    name: Optional[str] = None
    color: Optional[str] = None


class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

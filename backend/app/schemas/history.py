from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class HistoryBase(BaseModel):
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class History(HistoryBase):
    id: int
    changed_at: datetime
    user_id: int

    class Config:
        from_attributes = True

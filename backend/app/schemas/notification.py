from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class NotificationType(str, Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_STATUS_CHANGED = "task_status_changed"
    PROJECT_COLLABORATION = "project_collaboration"
    TASK_COMMENT = "task_comment"
    TASK_DUE_SOON = "task_due_soon"


class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str


class NotificationCreate(NotificationBase):
    related_task_id: Optional[int] = None
    related_project_id: Optional[int] = None


class Notification(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    read: bool = False
    read_at: Optional[datetime] = None
    related_task_id: Optional[int] = None
    related_project_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

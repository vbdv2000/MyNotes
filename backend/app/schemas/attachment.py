from datetime import datetime
from pydantic import BaseModel, Field


class AttachmentBase(BaseModel):
    filename: str = Field(..., max_length=255)
    content_type: str
    file_size: int


class AttachmentCreate(AttachmentBase):
    file_data: bytes


class Attachment(AttachmentBase):
    id: int
    task_id: int
    uploaded_at: datetime
    uploaded_by: int

    class Config:
        from_attributes = True

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from app.db.base import Base


class TaskAttachment(Base):
    __tablename__ = "task_attachments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # MIME type
    file_size = Column(Integer, nullable=False)  # Size in bytes
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_data = Column(LargeBinary, nullable=False)  # The actual file data

    # Relationships
    task = relationship("Task", back_populates="attachments")
    user = relationship("User")

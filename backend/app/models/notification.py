from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.schemas.notification import NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(NotificationType))
    title = Column(String, index=True)
    message = Column(String)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    related_task_id = Column(
        Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True
    )
    related_project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="notifications")
    task = relationship("Task", back_populates="notifications")
    project = relationship("Project", back_populates="notifications")

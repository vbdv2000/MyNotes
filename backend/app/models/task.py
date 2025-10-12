# backend/app/models/task.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.notification import Notification  # Import Notification model
import enum


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


# Table for Many-to-Many relationship between Tasks and Users (Assigned Users)
task_assigned = Table(
    "task_assigned",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    review = "review"
    done = "done"


class Task(Base):
    """
    SQLAlchemy model for the 'tasks' table.
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    status = Column(Enum(TaskStatus), default=TaskStatus.todo)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="tasks")

    # (ASSIGNED USERS) - Many-to-Many relationship with Users
    assigned_users = relationship(
        "User", secondary=task_assigned, back_populates="assigned_tasks"
    )

    # Tags
    tags = relationship("Tag", secondary="task_tag", back_populates="tasks")

    # History
    history = relationship(
        "TaskHistory", back_populates="task", cascade="all, delete-orphan"
    )

    # Notifications
    notifications = relationship(
        "Notification", back_populates="task", cascade="all, delete-orphan"
    )

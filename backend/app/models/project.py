from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.tag import project_tag
from app.models.history import ProjectHistory  # Import ProjectHistory model
from app.models.notification import Notification  # Import Notification model

# Table for Many-to-Many relationship between Projects and Users (Collaborators)
project_collaborator = Table(
    "project_collaborator",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # (Owner) - One-to-Many relationship with Users
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="owned_projects")

    # (Collaborators) - Many-to-Many relationship with Users
    collaborators = relationship(
        "User", secondary=project_collaborator, back_populates="collaborating_projects"
    )

    # (Tasks) - One-to-Many relationship with Tasks
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    # Tags
    tags = relationship("Tag", secondary=project_tag, back_populates="projects")

    # History
    history = relationship(
        "ProjectHistory", back_populates="project", cascade="all, delete-orphan"
    )

    # Notifications
    notifications = relationship(
        "Notification", back_populates="project", cascade="all, delete-orphan"
    )

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

# Many-to-Many relationships for tags
project_tag = Table(
    "project_tag",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

task_tag = Table(
    "task_tag",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False, unique=True)
    color = Column(String, default="#808080")  # Default gray color in hex
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tasks = relationship("Task", secondary=task_tag, back_populates="tags")
    projects = relationship("Project", secondary=project_tag, back_populates="tags")

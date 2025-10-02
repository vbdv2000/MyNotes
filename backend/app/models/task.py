# backend/app/models/task.py

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.db.base import Base

# Table for Many-to-Many relationship between Tasks and Users (Assigned Users)
task_assigned = Table(
    'task_assigned', Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class Task(Base):
    """
    SQLAlchemy model for the 'tasks' table.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    status = Column(String, default="To Do") # e.g., 'To Do', 'In Progress', 'Done'

    # Project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False) 
    project = relationship("Project", back_populates="tasks")

    # (ASSIGNED USERS) - Many-to-Many relationship with Users
    assigned_users = relationship(
        "User", 
        secondary=task_assigned, 
        back_populates="assigned_tasks"
    )
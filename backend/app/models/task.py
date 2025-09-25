# backend/app/models/task.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

class Task(Base):
    """
    SQLAlchemy model for the 'tasks' table.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    status = Column(String, default="To Do") # e.g., 'To Do', 'In Progress', 'Done'

    # Foreign key to link to the User model
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship to the User model
    owner = relationship("User", back_populates="tasks")
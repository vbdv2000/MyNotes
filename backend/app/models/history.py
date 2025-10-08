from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class TaskHistory(Base):
    __tablename__ = "task_history"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    field_name = Column(String, nullable=False)  # Which field was changed
    old_value = Column(String)  # Previous value
    new_value = Column(String)  # New value
    
    # Relationships
    task = relationship("Task", back_populates="history")
    user = relationship("User")

class ProjectHistory(Base):
    __tablename__ = "project_history"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    field_name = Column(String, nullable=False)  # Which field was changed
    old_value = Column(String)  # Previous value
    new_value = Column(String)  # New value
    
    # Relationships
    project = relationship("Project", back_populates="history")
    user = relationship("User")
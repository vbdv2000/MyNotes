# backend/app/models/user.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.project import project_collaborator 
from app.models.task import task_assigned

class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    owned_projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

    # Proyectos en los que Colabora (Collaborating Projects)
    collaborating_projects = relationship(
        "Project",
        secondary=project_collaborator,
        back_populates="collaborators"
    )
    
    # Tareas asignadas (Si tienes una relación Task.assigned_to)
    assigned_tasks = relationship(
        "Task", 
        secondary=task_assigned, 
        back_populates="assigned_users"
    )
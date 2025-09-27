from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.db.base import Base

# Table for Many-to-Many relationship between Projects and Users (Collaborators)
project_collaborator = Table(
    'project_collaborator', Base.metadata,
    Column('project_id', Integer, ForeignKey('project.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True)
)

class Project(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, default="")

    # (Owner) - One-to-Many relationship with Users
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    owner = relationship("User", back_populates="owned_projects")

    # (Collaborators) - Many-to-Many relationship with Users
    collaborators = relationship(
        "User", 
        secondary=project_collaborator, 
        back_populates="collaborating_projects"
    )
    
    # (Tasks) - One-to-Many relationship with Tasks
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
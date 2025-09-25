# backend/app/models/user.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base

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
    tasks = relationship("Task", back_populates="owner")
    # projects = relationship("Project", back_populates="owner")
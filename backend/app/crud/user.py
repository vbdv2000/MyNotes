from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# Crypt context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Retrieves a user by their ID."""
    stmt = select(User).where(User.id == user_id)
    return db.scalar(stmt)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieves a user by their email address."""
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)

def create_user(db: Session, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        is_superuser=user_in.is_superuser,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

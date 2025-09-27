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

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Retrieves all users with pagination."""
    stmt = select(User).offset(skip).limit(limit)
    return list(db.scalars(stmt))

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

def update_user(
    db: Session, 
    db_obj: User,
    obj_in: Union[UserUpdate, Dict[str, Any]]
) -> Optional[User]:
    """Updates a user's information."""
    obj_data = db_obj.dict()
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    # Hash password if it's provided in the update data
    if update_data.get("password"):
        from app.crud.user import get_password_hash
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]

    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_user(db: Session, db_obj: User) -> User:
    """Deletes a user by their ID."""
    db.delete(db_obj)
    db.commit()
    return db_obj

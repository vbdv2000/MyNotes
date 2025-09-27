from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate 
from app.crud import user as crud_user 

router = APIRouter()

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> UserSchema:
    """
    Creates a new user and checks if the email already exists.
    """
    # 1. Check if the email already exists
    user = crud_user.get_user_by_email(db, email=user_in.email)
    
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
        
    # 2. If it does not exist, create the user
    new_user = crud_user.create_user(db, user_in=user_in)
    return new_user

@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0, 
    limit: int = 100,
) -> Any:
    """
    Retrieves the list of all users with optional pagination.
    """
    users = crud_user.get_all_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieves a specific user by ID.
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return user

@router.patch("/{user_id}", response_model=UserSchema)
def update_user_endpoint(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Updates an existing user.
    """
    # 1. Get the existing user object
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # 2. Update the user
    user = crud_user.update_user(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Deletes a user by ID and returns 204 No Content."""
    
    user = crud_user.get_user(db, user_id=user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    crud_user.delete_user(db, db_obj=user)
    
    return 
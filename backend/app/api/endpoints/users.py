# app/api/endpoints/users.py

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.crud import user as crud_user
from app.core.security import get_current_user
from app.schemas.user import User

router = APIRouter(tags=["users"])

# --- CRUD Endpoints ---


@router.post(
    "/",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "newuser@example.com",
                        "full_name": "New User",
                        "is_active": True,
                        "is_superuser": False,
                    }
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {"example": {"detail": "Email already registered"}}
            },
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {"example": {"detail": "Not enough permissions"}}
            },
        },
    },
)
def create_new_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    """
    Creates a new user in the system.

    **Required Fields:**
    - email: Valid email address
    - password: Secure password (min 8 characters)

    **Optional Fields:**
    - full_name: User's full name
    - is_active: Whether the account is active (default: true)
    - is_superuser: Whether the user has admin privileges (default: false)

    **Permissions:**
    - Only authenticated users can create new users
    - Superusers can create other superusers
    """
    # Optional: restrict to superusers
    # if not current_user.is_superuser:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Only superusers can create new users"
    #     )

    # 1. Check if the email already exists
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    # 2. Create the user
    new_user = crud_user.create_user(db, user_in=user_in)
    return new_user


@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieves all users. Optional: restrict to superusers only.
    """
    # Optional restriction
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can view all users",
        )

    users = crud_user.get_all_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieves a specific user by ID.
    Only the user itself or a superuser can view.
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user",
        )

    return user


@router.patch("/{user_id}", response_model=UserSchema)
def update_user_endpoint(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Updates an existing user.
    Only the user itself or a superuser can update.
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    updated_user = crud_user.update_user(db, db_obj=user, obj_in=user_in)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deletes a user by ID.
    Only the user itself or a superuser can delete.
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )

    crud_user.delete_user(db, db_obj=user)
    return

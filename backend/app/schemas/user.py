from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.core.validators import validate_password, PasswordValidationError

# --- Base Schema for Relationships ---


class UserBase(BaseModel):
    id: Optional[int] = Field(None, description="Unique identifier of the user")
    email: EmailStr = Field(
        ..., description="User's email address", example="user@example.com"
    )
    full_name: Optional[str] = Field(
        None, description="User's full name", example="John Doe"
    )

    model_config = ConfigDict(from_attributes=True)


# --- Create and Update Schemas ---


class UserCreate(UserBase):
    """
    Schema for creating a new user with password validation
    """

    password: str = Field(
        ...,
        description="""User's password must:
        - Be at least 8 characters long
        - Contain at least one uppercase letter
        - Contain at least one lowercase letter
        - Contain at least one number
        - Contain at least one special character
        """,
        example="SecurePass123!",
    )
    is_active: bool = Field(True, description="Whether the user account is active")
    is_superuser: bool = Field(
        False, description="Whether the user has administrator privileges"
    )

    @field_validator("password")
    def validate_password_strength(cls, v):
        try:
            return validate_password(v)
        except PasswordValidationError as e:
            raise ValueError(str(e))

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "newuser@example.com",
                "full_name": "New User",
                "password": "SecurePass123!",
                "is_active": True,
                "is_superuser": False,
            }
        }
    }


class UserUpdate(UserBase):
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


# --- Read Schema (Excludes Password) ---


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

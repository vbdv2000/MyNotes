# app/api/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.token import Token
from app.core.logging import log_auth_event
from app.crud import user as crud_user
from app.core.security import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from datetime import timedelta

router = APIRouter(tags=["auth"])


@router.post(
    "/login",
    response_model=Token,
    responses={
        200: {
            "description": "Successful login",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect email or password"}
                }
            },
        },
    },
)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a JWT token.

    **Input:**
    - username: User's email address
    - password: User's password

    **Returns:**
    - access_token: JWT token valid for 24 hours
    - token_type: Type of token (bearer)
    """
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if not user:
        log_auth_event(
            event_type="login_failed",
            user_email=form_data.username,
            success=False,
            ip=request.client.host,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(form_data.password, user.hashed_password):
        log_auth_event(
            event_type="login_failed",
            user_email=form_data.username,
            success=False,
            ip=request.client.host,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )

    # Log successful login
    log_auth_event(
        event_type="login_success",
        user_email=user.email,
        success=True,
        ip=request.client.host,
    )

    return {"access_token": access_token, "token_type": "bearer"}

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import get_current_user
from app.schemas.notification import Notification
from app.crud import notification as crud_notification
from app.core.rate_limit import limiter, READ_LIMIT
from app.schemas.user import User

router = APIRouter(tags=["notifications"])


@router.get("/", response_model=List[Notification])
@limiter.limit(READ_LIMIT)
async def get_notifications(
    unread_only: bool = Query(False, description="Filter only unread notifications"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    """
    Retrieve notifications for the current user.
    """
    return crud_notification.get_user_notifications(
        db, current_user.id, skip=skip, limit=limit, unread_only=unread_only
    )


@router.post("/{notification_id}/read", response_model=Notification)
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a notification as read.
    """
    notification = crud_notification.mark_notification_as_read(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this notification",
        )
    return notification


@router.post("/mark-all-read", response_model=dict)
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark all notifications as read for the current user.
    """
    count = crud_notification.mark_all_as_read(db, current_user.id)
    return {"message": f"Marked {count} notifications as read"}

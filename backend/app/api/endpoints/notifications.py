from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Path
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.security import get_current_user
from app.schemas.notification import (
    Notification,
    NotificationCreate,
    NotificationType,
)
from app.crud import notification as crud_notification
from app.core.rate_limit import limiter, READ_LIMIT
from app.schemas.user import User

router = APIRouter(tags=["notifications"])


@router.get("/", response_model=List[Notification])
@limiter.limit(READ_LIMIT)
async def get_notifications(
    unread_only: bool = Query(False, description="Filter only unread notifications"),
    notification_type: Optional[NotificationType] = Query(
        None, description="Filter by notification type"
    ),
    skip: int = Query(0, ge=0, description="Skip first N notifications"),
    limit: int = Query(100, ge=1, le=100, description="Limit number of notifications"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    """
    Retrieve notifications for the current user with filtering options.
    """
    return crud_notification.get_user_notifications(
        db,
        current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        notification_type=notification_type,
    )


@router.get("/count", response_model=dict)
async def get_notifications_count(
    unread_only: bool = Query(False, description="Count only unread notifications"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the total count of notifications for the current user.
    """
    count = crud_notification.get_notifications_count(db, current_user.id, unread_only)
    return {"total": count}


@router.post("/", response_model=Notification, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new notification for the current user.
    """
    return crud_notification.create_notification(
        db,
        notification_in=notification,
        user_id=current_user.id,
    )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a notification.
    """
    notification = crud_notification.get_notification(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this notification",
        )
    crud_notification.delete_notification(db, notification_id)


@router.post("/{notification_id}/read", response_model=Notification)
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a notification as read.
    """
    notification = crud_notification.get_notification(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this notification",
        )
    return crud_notification.mark_notification_as_read(db, notification_id)


@router.post("/mark-all-read", response_model=dict)
async def mark_all_notifications_read(
    notification_type: Optional[NotificationType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark all notifications as read for the current user.
    Optionally filter by notification type.
    """
    count = crud_notification.mark_all_as_read(
        db, current_user.id, notification_type=notification_type
    )
    return {"message": f"Marked {count} notifications as read"}


@router.post("/bulk-delete", response_model=dict)
async def delete_multiple_notifications(
    notification_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Handles bulk deletion of notifications.
    """
    deleted_count = crud_notification.delete_multiple_notifications(
        db, notification_ids, current_user.id
    )
    return {"message": f"Successfully deleted {deleted_count} notifications"}

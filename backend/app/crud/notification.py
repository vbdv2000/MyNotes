from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


def create_notification(
    db: Session, notification_in: NotificationCreate, user_id: int
) -> Notification:
    """Creates a new notification."""
    db_notification = Notification(
        type=notification_in.type,
        title=notification_in.title,
        message=notification_in.message,
        user_id=user_id,
        related_task_id=notification_in.related_task_id,
        related_project_id=notification_in.related_project_id,
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def get_user_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    notification_type: Optional[str] = None,
) -> List[Notification]:
    """Gets all notifications for a user."""
    query = select(Notification).where(Notification.user_id == user_id)

    if unread_only:
        query = query.where(~Notification.read)

    if notification_type:
        query = query.where(Notification.type == notification_type)

    query = query.offset(skip).limit(limit)
    return list(db.scalars(query))


def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
    """Retrieves a single notification by its ID."""
    return db.get(Notification, notification_id)


def mark_notification_as_read(
    db: Session, notification_id: int
) -> Optional[Notification]:
    """Marks a notification as read."""
    notification = db.get(Notification, notification_id)
    if notification:
        notification.read = True
        notification.read_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)
    return notification


def mark_all_as_read(
    db: Session, user_id: int, notification_type: Optional[str] = None
) -> int:
    """Marks all notifications as read for a user efficiently."""

    # 1. Definir la sentencia de actualización
    stmt = (
        update(Notification)
        .where(Notification.user_id == user_id)
        .where(~Notification.read)
        .values(read=True, read_at=datetime.utcnow())
    )
    if notification_type:
        stmt = stmt.where(Notification.type == notification_type)

    result = db.execute(stmt, execution_options={"synchronize_session": False})

    db.commit()
    return result.rowcount


def delete_notification(db: Session, notification_id: int) -> Optional[Notification]:
    """Deletes a notification."""
    notification = db.get(Notification, notification_id)
    if notification:
        db.delete(notification)
        db.commit()
    return notification


def get_notifications_count(
    db: Session, user_id: int, unread_only: bool = False
) -> int:
    """Get the total count of notifications for a user."""
    query = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        query = query.where(~Notification.read)
    return len(list(db.scalars(query)))


def delete_multiple_notifications(
    db: Session, notification_ids: List[int], user_id: int
) -> int:
    """Delete multiple notifications at once, only if they belong to the user."""
    count = 0
    for notification_id in notification_ids:
        notification = get_notification(db, notification_id)
        if notification and notification.user_id == user_id:
            db.delete(notification)
            count += 1
    db.commit()
    return count

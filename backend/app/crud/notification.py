from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationType


def create_notification(
    db: Session, notification_in: NotificationCreate
) -> Notification:
    """Creates a new notification."""
    db_notification = Notification(
        type=notification_in.type,
        title=notification_in.title,
        message=notification_in.message,
        user_id=notification_in.user_id,
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
) -> List[Notification]:
    """Gets all notifications for a user."""
    query = select(Notification).where(Notification.user_id == user_id)

    if unread_only:
        query = query.where(Notification.read == False)

    query = query.offset(skip).limit(limit)
    return list(db.scalars(query))


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


def mark_all_as_read(db: Session, user_id: int) -> int:
    """Marks all notifications as read for a user."""
    stmt = select(Notification).where(
        Notification.user_id == user_id, Notification.read == False
    )
    unread = db.scalars(stmt).all()

    count = 0
    for notification in unread:
        notification.read = True
        notification.read_at = datetime.utcnow()
        count += 1

    db.commit()
    return count


def delete_notification(db: Session, notification_id: int) -> Optional[Notification]:
    """Deletes a notification."""
    notification = db.get(Notification, notification_id)
    if notification:
        db.delete(notification)
        db.commit()
    return notification

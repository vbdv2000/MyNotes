from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Retrieves a single task by its ID."""
    stmt = select(Task).where(Task.id == task_id)
    return db.scalar(stmt)


def get_project_tasks(
    db: Session, project_id: int, skip: int = 0, limit: int = 100
) -> List[Task]:
    """Retrieves tasks from a specific project with pagination."""
    stmt = select(Task).where(Task.project_id == project_id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    """
    Retrieves all tasks across all projects with pagination.
    Note: This method should be used cautiously and ideally replaced with get_project_tasks.
    """
    stmt = select(Task).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def get_tasks_by_tag(
    db: Session, tag_id: int, skip: int = 0, limit: int = 100
) -> List[Task]:
    """Retrieves tasks associated with a specific tag."""
    from app.models.tag import Tag

    stmt = (
        select(Task)
        .join(Tag, Task.tags)
        .where(Tag.id == tag_id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt))


def create_task(
    db: Session, task_in: TaskCreate, project_id: int, current_user_id: int = None
) -> Task:
    """Creates a new task in the database."""
    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date,
        project_id=project_id,
    )

    if task_in.assigned_user_ids:
        assigned_users = db.scalars(
            select(User).where(User.id.in_(task_in.assigned_user_ids))
        ).all()
        db_task.assigned_users.extend(assigned_users)

    if task_in.tag_ids:
        from app.models.tag import Tag

        tags = db.scalars(select(Tag).where(Tag.id.in_(task_in.tag_ids))).all()
        db_task.tags.extend(tags)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Create history entry for task creation
    if current_user_id:
        from app.models.history import TaskHistory

        history = TaskHistory(
            task_id=db_task.id,
            user_id=current_user_id,
            field_name="status",
            old_value=None,
            new_value=f"Task created with status: {task_in.status}",
        )
        db.add(history)
        db.commit()

    return db_task


def update_task(
    db: Session,
    db_obj: Task,
    obj_in: Union[TaskUpdate, Dict[str, Any]],
    current_user_id: int = None,
) -> Task:
    """Updates an existing Task object, handling assignment updates."""

    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    # Store original values for history
    original_values = {
        "status": db_obj.status,
        "priority": db_obj.priority,
        "title": db_obj.title,
        "description": db_obj.description,
        "due_date": db_obj.due_date,
    }

    if "assigned_user_ids" in update_data:
        new_assigned_user_ids = update_data.pop("assigned_user_ids")
        db_obj.assigned_users.clear()
        if new_assigned_user_ids:
            new_assigned_users = db.scalars(
                select(User).where(User.id.in_(new_assigned_user_ids))
            ).all()
            db_obj.assigned_users.extend(new_assigned_users)

    if "tag_ids" in update_data:
        from app.models.tag import Tag

        new_tag_ids = update_data.pop("tag_ids")
        db_obj.tags.clear()
        if new_tag_ids:
            new_tags = db.scalars(select(Tag).where(Tag.id.in_(new_tag_ids))).all()
            db_obj.tags.extend(new_tags)

    for field, value in update_data.items():
        if (
            field in original_values
            and original_values[field] != value
            and current_user_id
        ):
            # Create history entry for each changed field
            from app.models.history import TaskHistory

            history = TaskHistory(
                task_id=db_obj.id,
                user_id=current_user_id,
                field_name=field,
                old_value=str(original_values[field])
                if original_values[field]
                else None,
                new_value=str(value) if value else None,
            )
            db.add(history)

        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_task(db: Session, db_obj: Task) -> Task:
    """Deletes a task."""
    db.delete(db_obj)
    db.commit()
    return db_obj

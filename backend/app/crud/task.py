from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Retrieves a single task by its ID."""
    stmt = select(Task).where(Task.id == task_id)
    return db.scalar(stmt)

def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    """Retrieves a list of tasks with pagination."""
    stmt = select(Task).offset(skip).limit(limit)
    return list(db.scalars(stmt))

def create_task(db: Session, task_in: TaskCreate) -> Task:
    """Creates a new task in the database."""
    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        owner_id=task_in.owner_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(
    db: Session, db_obj: Task, obj_in: Union[TaskUpdate, Dict[str, Any]]
) -> Task:
    """
    Updates an existing Task object with new data.
    """
    obj_data = db_obj.dict()
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        # Pydantic utility to get a dict of fields that were set (not None)
        update_data = obj_in.model_dump(exclude_unset=True)

    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_task(db: Session, db_obj: Task) -> Task:
    """
    Deletes a Task object.
    """
    db.delete(db_obj)
    db.commit()
    return db_obj
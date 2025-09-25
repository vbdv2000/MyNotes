from typing import List, Optional

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
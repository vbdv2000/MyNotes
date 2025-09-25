from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Retrieves a single task by its ID."""
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    """Retrieves a list of tasks with pagination."""
    return db.query(Task).offset(skip).limit(limit).all()

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
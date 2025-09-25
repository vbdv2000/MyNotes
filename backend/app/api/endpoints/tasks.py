from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.task import TaskCreate, Task
from app.crud.task import create_task, get_tasks

router = APIRouter()

@router.post("/", response_model=Task)
def create_new_task(
    *,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
) -> Any:
    """
    Create a new task.
    """
    task = create_task(db, task_in=task_in)
    return task

@router.get("/", response_model=List[Task])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve a list of tasks.
    """
    tasks = get_tasks(db, skip=skip, limit=limit)
    return tasks
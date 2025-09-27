from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.task import TaskCreate, Task, TaskUpdate, Task as TaskSchema
from app.crud import task as crud_task

router = APIRouter()

@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
def create_new_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Create a new task.
    """
    task = crud_task.create_task(db, task_in=task_in)
    return task

@router.get("/", response_model=List[TaskSchema])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve a list of tasks with optional pagination.
    """
    tasks = crud_task.get_tasks(db, skip=skip, limit=limit)
    return tasks

@router.get("/{task_id}", response_model=TaskSchema)
def read_task_by_id(
    *,
    db: Session = Depends(get_db),
    task_id: int,
) -> Any:
    """
    Get a specific task by ID.
    """
    task = crud_task.get_task(db, task_id=task_id)
    return task

@router.patch("/{task_id}", response_model=TaskSchema)
def update_task_endpoint(
    task_id: int,
    task_in: TaskUpdate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Updates an existing task.
    """
    task = crud_task.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task not found"
        )
    
    task = crud_task.update_task(db, db_obj=task, obj_in=task_in)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Deletes a specific task by ID.
    """
    task = crud_task.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    crud_task.delete_task(db, db_obj=task)

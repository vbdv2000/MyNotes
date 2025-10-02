# app/api/endpoints/tasks.py

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema
from app.crud import task as crud_task
from app.crud import project as crud_project
from app.core.security import get_current_user
from app.schemas.user import User

# Router configuration
router = APIRouter(tags=["tasks"])

# --- Helper Functions ---


def check_users_in_project(db: Session, project_id: int, user_ids: List[int]):
    """
    Ensures that all users in user_ids are members of the project.
    Raises 400 if any user is not part of the project.
    """
    project = crud_project.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    project_user_ids = [project.owner_id] + [u.id for u in project.collaborators]
    for uid in user_ids:
        if uid not in project_user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User ID {uid} is not a valid team member for this project",
            )


# --- CRUD Endpoints ---


@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new task assigned to valid project members.
    Only participants of the project can create tasks.
    """
    project = crud_project.get_project(db, project_id=task_in.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # Only owner or collaborators can create tasks
    if current_user.id != project.owner_id and current_user.id not in [
        u.id for u in project.collaborators
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a project participant",
        )

    # Validate assigned users
    if task_in.assigned_user_ids:
        check_users_in_project(db, task_in.project_id, task_in.assigned_user_ids)

    task = crud_task.create_task(db, task_in=task_in)
    return task


@router.get("/", response_model=List[TaskSchema])
def read_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve tasks visible to current_user (owner or collaborator)
    """
    all_tasks = crud_task.get_tasks(db, skip=skip, limit=limit)
    visible_tasks = [
        t
        for t in all_tasks
        if current_user.id == t.project.owner_id
        or current_user.id in [u.id for u in t.project.collaborators]
    ]
    return visible_tasks


@router.get("/{task_id}", response_model=TaskSchema, status_code=status.HTTP_200_OK)
def read_task_by_id(
    *,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get a specific task by ID if current_user is part of the project.
    """
    task = crud_task.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    project = crud_project.get_project(db, task.project_id)
    if current_user.id != project.owner_id and current_user.id not in [
        u.id for u in project.collaborators
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a project participant",
        )

    return task


@router.patch("/{task_id}", response_model=TaskSchema)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates a task. Only project participants can update.
    Assigned users must be part of the project.
    """
    task = crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    project = crud_project.get_project(db, task.project_id)
    if current_user.id != project.owner_id and current_user.id not in [
        u.id for u in project.collaborators
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a project participant",
        )

    if task_in.assigned_user_ids is not None:
        check_users_in_project(db, project.id, task_in.assigned_user_ids)

    updated_task = crud_task.update_task(db, db_obj=task, obj_in=task_in)
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Deletes a task. Only project owner can delete.
    """
    task = crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    project = crud_project.get_project(db, task.project_id)
    if current_user.id != project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can delete tasks",
        )

    crud_task.delete_task(db, db_obj=task)
    return

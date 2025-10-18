from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.base import get_db
from app.crud import project as crud_project
from app.crud import user as crud_user
from app.core.security import get_current_user
from app.schemas.user import User
from app.schemas.task import Task as TaskSchema, TaskCreate, TaskUpdate
from app.schemas.history import History
from app.crud import task as crud_task
from app.crud import tag as crud_tag
from app.models.tag import Tag

router = APIRouter(tags=["tasks"])
# --- Helper Function for ID Validation ---


def check_user_exists(db: Session, user_ids: List[int]):
    """Checks if all IDs in the list exist in the User table."""
    for user_id in user_ids:
        if not crud_user.get_user(db, user_id=user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User ID {user_id} not found.",
            )


# Incluir el router de tareas con el project_id como dependencia
@router.get("/{project_id}/tasks", response_model=List[TaskSchema])
def get_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
) -> Any:
    """
    Retrieve tasks for a specific project
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # Check if user is owner or collaborator
    if current_user.id != project.owner_id and current_user.id not in [
        u.id for u in project.collaborators
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a project participant"
        )

    tasks = crud_task.get_project_tasks(
        db, project_id=project_id, skip=skip, limit=limit
    )
    return tasks


@router.get("/{project_id}/tasks/{task_id}", response_model=TaskSchema)
def get_project_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get a specific task from a project
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    task = crud_task.get_task(db, task_id=task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in this project",
        )

    # Check if user is owner or collaborator
    if current_user.id != project.owner_id and current_user.id not in [
        u.id for u in project.collaborators
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a project participant"
        )

    return task


@router.post(
    "/{project_id}/tasks",
    response_model=TaskSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_project_task(
    project_id: int,
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Creates a new task in the specified project.
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # Only owner or collaborators can create tasks
    if current_user.id != project.owner_id and current_user.id not in [
        u.id for u in project.collaborators
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a project participant"
        )

    # Validate assigned users
    if task_in.assigned_user_ids:
        check_user_exists(db, task_in.assigned_user_ids)
        for user_id in task_in.assigned_user_ids:
            if user_id not in [project.owner_id] + [
                u.id for u in project.collaborators
            ]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User {user_id} is not a member of this project",
                )

    # Validate tags if provided
    if task_in.tag_ids:
        existing_tags = db.query(Tag).filter(Tag.id.in_(task_in.tag_ids)).all()
        if len(existing_tags) != len(task_in.tag_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Some tags do not exist"
            )

    task = crud_task.create_task(
        db=db, task_in=task_in, project_id=project_id, current_user_id=current_user.id
    )
    return task


@router.put("/{project_id}/tasks/{task_id}", response_model=TaskSchema)
def update_project_task(
    project_id: int,
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Updates an existing task in the project.
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    task = crud_task.get_task(db, task_id=task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in this project",
        )

    # Only owner or collaborators can update tasks
    if current_user.id != project.owner_id and current_user.id not in [
        u.id for u in project.collaborators
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a project participant"
        )

    # Validate assigned users if provided
    if task_in.assigned_user_ids is not None:
        check_user_exists(db, task_in.assigned_user_ids)
        for user_id in task_in.assigned_user_ids:
            if user_id not in [project.owner_id] + [
                u.id for u in project.collaborators
            ]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User {user_id} is not a member of this project",
                )

    # Validate tags if provided
    if task_in.tag_ids is not None:
        existing_tags = db.query(Tag).filter(Tag.id.in_(task_in.tag_ids)).all()
        if len(existing_tags) != len(task_in.tag_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Some tags do not exist"
            )

    task = crud_task.update_task(
        db=db, db_obj=task, obj_in=task_in, current_user_id=current_user.id
    )
    return task


@router.delete("/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Deletes a task from a project.
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    task = crud_task.get_task(db, task_id=task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in this project",
        )

    # Only project owner can delete tasks
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can delete tasks",
        )

    crud_task.delete_task(db, task)
    return None


@router.get("/{project_id}/tasks/{task_id}/history", response_model=List[History])
def get_task_history(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get the history of changes for a specific task.
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    task = crud_task.get_task(db, task_id=task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in this project",
        )

    # Only owner or collaborators can view history
    if current_user.id != project.owner_id and current_user.id not in [
        u.id for u in project.collaborators
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not a project participant"
        )

    return task.history


@router.get("/{tag_id}/tasks", response_model=List[TaskSchema])
def get_tasks_by_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get all tasks that have this tag.
    """
    tag = crud_tag.get_tag(db, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return crud_task.get_tasks_by_tag(db, tag_id, skip=skip, limit=limit)

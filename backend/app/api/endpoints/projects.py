from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.base import get_db
from app.crud import project as crud_project
from app.crud import user as crud_user
from app.schemas.project import Project as ProjectSchema, ProjectCreate, ProjectUpdate
from app.core.security import get_current_user
from app.schemas.user import User
from app.schemas.task import Task as TaskSchema, TaskCreate, TaskUpdate
from app.schemas.history import History
from app.crud import task as crud_task
from app.models.tag import Tag

router = APIRouter(tags=["projects"])


# Incluir el router de tareas con el project_id como dependencia
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


# --- Helper Function for ID Validation ---


def check_user_exists(db: Session, user_ids: List[int]):
    """Checks if all IDs in the list exist in the User table."""
    for user_id in user_ids:
        if not crud_user.get_user(db, user_id=user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User ID {user_id} not found.",
            )


# --- CRUD Endpoints ---


@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
def create_project_endpoint(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Creates a new project. Only the authenticated user can be the owner.
    """
    project_in.owner_id = current_user.id  # fuerza owner
    if project_in.collaborator_ids:
        check_user_exists(db, project_in.collaborator_ids)
        if current_user.id in project_in.collaborator_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner cannot be listed as a collaborator.",
            )
    project = crud_project.create_project(db, project_in=project_in)
    return project


@router.get("/{project_id}", response_model=ProjectSchema)
def read_project_by_id_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieves a specific project by ID. Only participants can view.
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # Check if user is owner or collaborator
    participant_ids = [project.owner_id] + [u.id for u in project.collaborators]
    if current_user.id not in participant_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this project.",
        )

    return project


@router.get("/", response_model=List[ProjectSchema])
def read_all_projects_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieves a list of projects where the current user is owner or collaborator.
    """
    projects = crud_project.get_all_projects(db)
    # Filter only projects where current_user is owner or collaborator
    visible_projects = [
        p
        for p in projects
        if current_user.id == p.owner_id
        or current_user.id in [u.id for u in p.collaborators]
    ]
    return visible_projects


@router.patch("/{project_id}", response_model=ProjectSchema)
def update_project_endpoint(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Updates an existing project. Only the owner can update.
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can update the project.",
        )

    # Validate collaborators if provided
    if project_in.collaborator_ids is not None:
        if project.owner_id in project_in.collaborator_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner cannot be listed as a collaborator.",
            )
        check_user_exists(db, project_in.collaborator_ids)

    updated_project = crud_project.update_project(db, db_obj=project, obj_in=project_in)
    return updated_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_endpoint(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Deletes a specific project by ID. Only the owner can delete.
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can delete the project.",
        )

    crud_project.delete_project(db, db_obj=project)
    return

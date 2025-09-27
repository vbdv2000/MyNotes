from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema
from app.crud import task as crud_task
from app.crud import project as crud_project

# Configuración del Router
router = APIRouter(prefix="/tasks", tags=["tasks"])

# --- Business Logic Validation Helper ---

def check_assigned_users_validity(db: Session, project_id: int, assigned_user_ids: List[int]):
    """
    Checks if all assigned_user_ids are either the project owner or a collaborator.
    Raises 404 if Project is not found.
    Raises 400 if any assigned user is not a valid team member.
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    valid_user_ids = {project.owner_id}
    valid_user_ids.update(c.id for c in project.collaborators)

    # 2. Verify each assigned user ID
    for user_id in assigned_user_ids:
        if user_id not in valid_user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User ID {user_id} is not a valid team member (Owner/Collaborator) for this project."
            )
    return project 

# --- CRUD Endpoints ---

@router.post("/", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
def create_new_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Create a new task, requiring it to belong to a project and validating assigned users.
    """
    check_assigned_users_validity(db, task_in.project_id, task_in.assigned_user_ids)
    
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

@router.get("/{task_id}", response_model=TaskSchema, status_code=status.HTTP_200_OK)
def read_task_by_id(
    *,
    db: Session = Depends(get_db),
    task_id: int,
) -> Any:
    """
    Get a specific task by ID.
    """
    task = crud_task.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task

@router.patch("/{task_id}", response_model=TaskSchema)
def update_task_endpoint(
    task_id: int,
    task_in: TaskUpdate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Updates an existing task and validates new assigned users if provided.
    """
    task = crud_task.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task not found"
        )
    
    if task_in.assigned_user_ids is not None:
        check_assigned_users_validity(db, task.project_id, task_in.assigned_user_ids)

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
    return

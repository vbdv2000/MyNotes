from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.base import get_db
from app.crud import project as crud_project
from app.crud import user as crud_user
from app.schemas.project import Project as ProjectSchema, ProjectCreate, ProjectUpdate

router = APIRouter(tags=["projects"])

# --- Helper Function for ID Validation ---

def check_user_exists(db: Session, user_ids: List[int]):
    """Checks if all IDs in the list exist in the User table."""
    for user_id in user_ids:
        if not crud_user.get_user(db, user_id=user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User ID {user_id} not found."
            )

# --- CRUD Endpoints ---

@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
def create_project_endpoint(
    project_in: ProjectCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Creates a new project, validates owner and initial collaborators.
    """
    # 1. Validate Owner ID
    if not crud_user.get_user(db, user_id=project_in.owner_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Owner ID {project_in.owner_id} not found."
        )
    
    # 2. Validate Collaborators if provided
    if project_in.collaborator_ids:
        if project_in.owner_id in project_in.collaborator_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner cannot be listed as a collaborator."
            )
        check_user_exists(db, project_in.collaborator_ids)
    
    # 3. Create the Project
    project = crud_project.create_project(db, project_in=project_in)
    return project

@router.get("/{project_id}", response_model=ProjectSchema)
def read_project_by_id_endpoint(project_id: int, db: Session = Depends(get_db)) -> Any:
    """
    Retrieves a specific project by ID.
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

@router.get("/", response_model=List[ProjectSchema])
def read_all_projects_endpoint(db: Session = Depends(get_db)) -> Any:
    """
    Retrieves a list of all projects.
    """
    projects = crud_project.get_all_projects(db)
    return projects

@router.patch("/{project_id}", response_model=ProjectSchema)
def update_project_endpoint(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Updates an existing project, validating new collaborators if provided.
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Validar Colaboradores si se intenta actualizar la lista (puede ser una lista vacía para limpiar)
    if project_in.collaborator_ids is not None:
        if project.owner_id in project_in.collaborator_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner cannot be listed as a collaborator."
            )
        check_user_exists(db, project_in.collaborator_ids)
    
    updated_project = crud_project.update_project(db, db_obj=project, obj_in=project_in)
    return updated_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_endpoint(project_id: int, db: Session = Depends(get_db)) -> None:
    """
    Deletes a specific project by ID.
    """
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    crud_project.delete_project(db, db_obj=project)
    return
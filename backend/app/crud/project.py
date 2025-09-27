from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.project import Project
from app.models.user import User 
from app.schemas.project import ProjectCreate, ProjectUpdate

def get_project(db: Session, project_id: int) -> Optional[Project]:
    """Retrieves a project by ID."""
    stmt = select(Project).where(Project.id == project_id)
    return db.scalar(stmt)

def get_all_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    """Retrieves all projects with pagination."""
    stmt = select(Project).offset(skip).limit(limit)
    return list(db.scalars(stmt))

def create_project(db: Session, project_in: ProjectCreate) -> Project:
    """Creates a new project and sets initial collaborators."""
    db_project = Project(
        title=project_in.title,
        description=project_in.description,
        owner_id=project_in.owner_id
    )

    if project_in.collaborator_ids:
        collaborators = db.scalars(
            select(User).where(User.id.in_(project_in.collaborator_ids))
        ).all()
        db_project.collaborators.extend(collaborators)

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(
    db: Session, 
    db_obj: Project,
    obj_in: Union[ProjectUpdate, Dict[str, Any]]
) -> Project:
    """Updates an existing Project object, handling collaborator updates."""
    
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True) 

    if "collaborator_ids" in update_data:
        new_collaborator_ids = update_data.pop("collaborator_ids")
        
        db_obj.collaborators.clear()
        
        if new_collaborator_ids:
            new_collaborators = db.scalars(
                select(User).where(User.id.in_(new_collaborator_ids))
            ).all()
            db_obj.collaborators.extend(new_collaborators)

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_project(db: Session, db_obj: Project) -> Project:
    """Deletes a project."""
    db.delete(db_obj)
    db.commit()
    return db_obj
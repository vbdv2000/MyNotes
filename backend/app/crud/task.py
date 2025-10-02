from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.task import Task
from app.models.user import User
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
        status=task_in.status,
        project_id=task_in.project_id
    )

    if task_in.assigned_user_ids:
        assigned_users = db.scalars(
            select(User).where(User.id.in_(task_in.assigned_user_ids))
        ).all()
        db_task.assigned_users.extend(assigned_users)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(
    db: Session, 
    db_obj: Task,
    obj_in: Union[TaskUpdate, Dict[str, Any]]
) -> Task:
    """Updates an existing Task object, handling assignment updates."""
    
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True) 

    if "assigned_user_ids" in update_data:
        new_assigned_user_ids = update_data.pop("assigned_user_ids")
        
        db_obj.assigned_users.clear()
        
        if new_assigned_user_ids:
            new_assigned_users = db.scalars(
                select(User).where(User.id.in_(new_assigned_user_ids))
            ).all()
            db_obj.assigned_users.extend(new_assigned_users)

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_task(db: Session, db_obj: Task) -> Task:
    """Deletes a task."""
    db.delete(db_obj)
    db.commit()
    return db_obj
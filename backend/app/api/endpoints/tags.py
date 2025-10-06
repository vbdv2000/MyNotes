from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.tag import TagCreate, TagUpdate, Tag as TagSchema
from app.models.tag import Tag
from app.crud import tag as crud_tag
from app.crud import task as crud_task
from app.core.security import get_current_user
from app.schemas.user import User
import re

# Router configuration
router = APIRouter(tags=["tags"])

# Constants
COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"


def validate_color(color: str) -> None:
    """Validate hex color format."""
    if not re.match(COLOR_PATTERN, color):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid color format. Must be a valid hex color (e.g., #FF0000)",
        )


@router.post("/", response_model=TagSchema, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_in: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new tag.
    Only users with permissions can create tags.
    """
    validate_color(tag_in.color)

    # Check if a tag with this name already exists (case-insensitive)
    existing_tag = db.query(Tag).filter(Tag.name.ilike(tag_in.name)).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name {tag_in.name} already exists",
        )

    return crud_tag.create_tag(db, tag_in=tag_in)


@router.get("/", response_model=List[TagSchema])
def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search tags by name"),
):
    """
    Retrieve tags with optional search and pagination.
    """
    return crud_tag.get_tags(db, skip=skip, limit=limit, search=search)


@router.get("/count", response_model=dict)
def get_tags_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get total count of tags.
    """
    count = crud_tag.get_tags_count(db)
    return {"total": count}


@router.get("/{tag_id}", response_model=TagSchema)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific tag by ID.
    """
    tag = crud_tag.get_tag(db, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return tag


@router.put("/{tag_id}", response_model=TagSchema)
def update_tag(
    tag_id: int,
    tag_in: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a tag.
    Only users with permissions can update tags.
    """
    tag = crud_tag.get_tag(db, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )

    if tag_in.color:
        validate_color(tag_in.color)

    if tag_in.name and tag_in.name != tag.name:
        existing_tag = db.query(Tag).filter(Tag.name.ilike(tag_in.name)).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name {tag_in.name} already exists",
            )

    return crud_tag.update_tag(db, db_obj=tag, obj_in=tag_in)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a tag.
    Only users with permissions can delete tags.
    Will remove the tag from all tasks and projects.
    """
    tag = crud_tag.get_tag(db, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    crud_tag.delete_tag(db, tag_id=tag_id)


@router.get("/{tag_id}/tasks", response_model=List[dict])
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

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.tag import TagCreate, TagUpdate, Tag as TagSchema
from app.models.tag import Tag
from app.crud import tag as crud_tag
from app.core.security import get_current_user
from app.schemas.user import User

# Router configuration
router = APIRouter(tags=["tags"])


@router.post("/", response_model=TagSchema, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_in: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new tag.
    """
    # Check if a tag with this name already exists
    existing_tag = db.query(Tag).filter(Tag.name == tag_in.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name {tag_in.name} already exists"
        )
        
    return crud_tag.create_tag(db, tag_in=tag_in)


@router.get("/", response_model=List[TagSchema])
def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve all tags.
    """
    return crud_tag.get_tags(db, skip=skip, limit=limit)


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
    """
    tag = crud_tag.get_tag(db, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
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
    """
    tag = crud_tag.get_tag(db, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    crud_tag.delete_tag(db, tag_id=tag_id)
    return

from sqlalchemy import select
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate


def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
    stmp = select(Tag).where(Tag.id == tag_id)
    return db.scalar(stmp)


def get_tags(
    db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None
) -> List[Tag]:
    stmp = select(Tag).offset(skip).limit(limit)
    if search:
        stmp = stmp.where(Tag.name.ilike(f"%{search}%"))

    return list(db.scalars(stmp))


def create_tag(db: Session, *, tag_in: TagCreate) -> Tag:
    db_tag = Tag(name=tag_in.name, color=tag_in.color)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def update_tag(db: Session, *, db_obj: Tag, obj_in: TagUpdate) -> Tag:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    for field in update_data:
        setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_tag(db: Session, *, tag_id: int) -> None:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()

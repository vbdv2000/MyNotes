from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Query,
    Response,
)
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.security import get_current_user
from app.schemas.attachment import Attachment
from app.crud import attachment as crud_attachment
from app.schemas.user import User
import os
import aiofiles
from pathlib import Path

router = APIRouter(prefix="/api/attachments", tags=["attachments"])

# Configuration constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "image/jpeg",
    "image/png",
    "image/gif",
]

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def validate_file(file: UploadFile) -> None:
    """Validate file size and type."""
    # Check file size
    content = await file.read()
    await file.seek(0)  # Reset file pointer
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / 1024 / 1024}MB",
        )

    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type {file.content_type} not allowed",
        )


@router.post(
    "/{task_id}", response_model=Attachment, status_code=status.HTTP_201_CREATED
)
async def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload an attachment for a task.
    Only project members can upload attachments.
    """
    await validate_file(file)

    # Save file and create attachment record
    file_path = UPLOAD_DIR / f"{task_id}_{file.filename}"
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    return crud_attachment.create_attachment(
        db,
        task_id=task_id,
        filename=file.filename,
        file_path=str(file_path),
        content_type=file.content_type,
        file_size=len(content),
        uploader_id=current_user.id,
    )


@router.get("/{task_id}", response_model=List[Attachment])
async def get_task_attachments(
    task_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all attachments for a specific task.
    Only project members can view attachments.
    """
    return crud_attachment.get_task_attachments(db, task_id, skip=skip, limit=limit)


@router.get("/{task_id}/{attachment_id}/download")
async def download_attachment(
    task_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download a specific attachment.
    Only project members can download attachments.
    """
    attachment = crud_attachment.get_attachment(db, attachment_id)
    if not attachment or attachment.task_id != task_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
        )

    try:
        async with aiofiles.open(attachment.file_path, "rb") as f:
            content = await f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found on server"
        )

    return Response(
        content=content,
        media_type=attachment.content_type,
        headers={"Content-Disposition": f"attachment; filename={attachment.filename}"},
    )


@router.delete("/{task_id}/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    task_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an attachment.
    Only the attachment uploader or project owner can delete attachments.
    """
    attachment = crud_attachment.get_attachment(db, attachment_id)
    if not attachment or attachment.task_id != task_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found"
        )

    if attachment.uploader_id != current_user.id:
        # Check if user is project owner
        task = crud_attachment.get_task(db, task_id)
        if task.project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this attachment",
            )

    # Delete file from storage
    try:
        os.remove(attachment.file_path)
    except FileNotFoundError:
        pass  # File already gone, continue with DB cleanup

    crud_attachment.delete_attachment(db, attachment_id)


@router.post("/{task_id}/bulk-delete", response_model=dict)
async def bulk_delete_attachments(
    task_id: int,
    attachment_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete multiple attachments at once.
    Only the attachment uploader or project owner can delete attachments.
    """
    deleted_count = 0
    for attachment_id in attachment_ids:
        try:
            await delete_attachment(task_id, attachment_id, db, current_user)
            deleted_count += 1
        except HTTPException as e:
            if e.status_code not in [
                status.HTTP_404_NOT_FOUND,
                status.HTTP_403_FORBIDDEN,
            ]:
                raise

    return {"message": f"Successfully deleted {deleted_count} attachments"}

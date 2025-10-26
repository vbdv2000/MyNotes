from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.tag import TagCreate, TagUpdate, Tag as TagSchema
from app.models.tag import Tag

# 💡 Asegúrate de tener crud_project para buscar proyectos
from app.crud import tag as crud_tag, project as crud_project
from app.core.security import get_current_user
from app.schemas.user import User
import re

# Router configuration
router = APIRouter(tags=["tags"])

# Constants
COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"


# --- Utility Functions (Maintain) ---
def validate_color(color: str) -> None:
    """Validate hex color format."""
    if not re.match(COLOR_PATTERN, color):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid color format. Must be a valid hex color (e.g., #FF0000)",
        )


# -------------------------------------------------------------------------
# 💡 ENDPOINTS: Siempre anidados a Project ID
# -------------------------------------------------------------------------


@router.post("/tags", response_model=TagSchema, status_code=status.HTTP_201_CREATED)
def create_and_associate_tag(
    project_id: int,
    tag_in: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea una nueva Tag y la asocia inmediatamente al proyecto especificado.
    Reemplaza el antiguo POST global.
    """
    validate_color(tag_in.color)

    # 1. Verificar si el proyecto existe
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # 2. Reutilizar Tag si existe globalmente por nombre (para mantener unicidad de Tag)
    tag = crud_tag.get_tag_by_name(db, name=tag_in.name)
    if not tag:
        # Crear la Tag si no existe
        tag = crud_tag.create_tag(db, tag_in=tag_in)

    # 3. Asociar la Tag al Proyecto si aún no está asociada
    if tag not in project.tags:
        project.tags.append(tag)
        db.commit()
        db.refresh(project)

    return tag


@router.get("/tags", response_model=List[TagSchema])
def get_project_tags(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search tags by name"),
):
    """
    Obtiene SÓLO las Tags asociadas al proyecto específico. Reemplaza el antiguo GET global.
    """
    # 1. Verificar si el proyecto existe
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # 2. Obtener tags (filtradas por búsqueda si es necesario)
    tags = project.tags
    if search:
        search_lower = search.lower()
        tags = [tag for tag in tags if search_lower in tag.name.lower()]

    # Nota: Si se requiere paginación, debe implementarse aquí también
    return tags


@router.get("/tags/{tag_id}", response_model=TagSchema)
def get_tag_in_project(
    project_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtiene una tag específica si pertenece al proyecto. Reemplaza el GET/{tag_id} global.
    """
    # 1. Verificar si el proyecto existe
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # 2. Buscar la tag y verificar pertenencia al proyecto
    tag = crud_tag.get_tag(db, tag_id=tag_id)
    if not tag or tag not in project.tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found in this project",
        )

    return tag


@router.put("/tags/{tag_id}", response_model=TagSchema)
def update_tag_in_project(
    project_id: int,
    tag_id: int,
    tag_in: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Actualiza una tag existente si pertenece al proyecto. Reemplaza el PUT/{tag_id} global.
    """
    # 1. Verificar si el proyecto existe
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # 2. Buscar la tag y verificar pertenencia al proyecto
    tag = crud_tag.get_tag(db, tag_id=tag_id)
    if not tag or tag not in project.tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found in this project",
        )

    # 3. Validaciones de actualización
    if tag_in.color:
        validate_color(tag_in.color)
    if tag_in.name and tag_in.name != tag.name:
        existing_tag = crud_tag.get_tag_by_name(db, name=tag_in.name)
        if existing_tag and existing_tag.id != tag_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name {tag_in.name} already exists",
            )

    return crud_tag.update_tag(db, db_obj=tag, obj_in=tag_in)


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag_from_project(
    project_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Elimina la asociación de una Tag con el proyecto.
    Si la Tag ya no está asociada a ningún proyecto/tarea, puede ser eliminada completamente (lógica a añadir en CRUD).
    Reemplaza el DELETE/{tag_id} global.
    """
    # 1. Verificar si el proyecto existe
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # 2. Buscar la tag y verificar pertenencia al proyecto
    tag = crud_tag.get_tag(db, tag_id=tag_id)
    if not tag or tag not in project.tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found in this project",
        )

    # 3. Eliminar la asociación (Many-to-Many)
    project.tags.remove(tag)
    db.commit()

    # 💡 Lógica opcional de limpieza: Si la tag ya no está en uso en NINGÚN proyecto/tarea, eliminarla de la DB.
    if not tag.projects and not tag.tasks:
        crud_tag.delete_tag(db, tag_id=tag_id)

    return

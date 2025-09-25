from pydantic import BaseModel
from typing import Optional

# Propiedades compartidas entre modelos
class TaskBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "To Do"  # Valor por defecto

# Propiedades para crear una nueva tarea (requiere título y el ID del propietario)
class TaskCreate(TaskBase):
    title: str
    owner_id: int

# Propiedades para actualizar una tarea
class TaskUpdate(TaskBase):
    pass

# Propiedades que se leen de la base de datos (con el ID y owner_id)
class TaskInDBBase(TaskBase):
    id: Optional[int] = None
    owner_id: int

    class Config:
        from_attributes = True

# Modelo de respuesta pública de la API
class Task(TaskInDBBase):
    pass
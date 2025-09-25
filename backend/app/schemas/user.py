from pydantic import BaseModel, EmailStr
from typing import Optional

# Propiedades compartidas entre modelos
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None

# Propiedades para crear un nuevo usuario (requiere email y password)
class UserCreate(UserBase):
    email: EmailStr
    password: str

# Propiedades para actualizar un usuario (password opcional)
class UserUpdate(UserBase):
    password: Optional[str] = None

# Propiedades que se leen de la base de datos (con el ID)
class UserInDBBase(UserBase):
    id: Optional[int] = None
    
    class Config:
        from_attributes = True

# Modelo de respuesta pública de la API
class User(UserInDBBase):
    pass
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base, get_db

# Configuración de la Base de Datos de Prueba (SQLite en archivo)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db" 

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# === Override de Dependencias ===

def override_get_db():
    """Función para sobreescribir la dependencia de base de datos."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# === Fixtures de Base de Datos y Cliente ===

@pytest.fixture()
def db():
    """
    Crea las tablas, proporciona una sesión y elimina todas las tablas 
    después de cada test para garantizar aislamiento. (Scope default: function)
    """
    # 1. Crear las tablas (esquema limpio)
    Base.metadata.create_all(bind=engine)
    
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        # 2. Cerrar la sesión
        db_session.close()
        # 3. Eliminar TODAS las tablas (limpieza total)
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db): # <--- Ahora depende de 'db' para forzar la inicialización
    """
    Proporciona un cliente de prueba de FastAPI que usa la base de datos de prueba.
    """
    # Aplicar el override antes de que el TestClient se ejecute
    app.dependency_overrides[get_db] = override_get_db
    
    # Iniciar el TestClient
    with TestClient(app) as client:
        yield client

    # Limpieza: Eliminar el override después de que el test termine
    app.dependency_overrides.clear()
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash, create_access_token

# Configuration of the test database
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
    Creates a new database session for a test.
    This fixture also creates all tables before the test and drops them after.
    """
    # 1. Crear las tablas (esquema limpio)
    Base.metadata.create_all(bind=engine)

    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        # 2. Close the session
        db_session.close()
        # 3. Remove all tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    """
    Provides a FastAPI test client that uses the test database.
    """
    # Apply the override before the TestClient is run
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# --- Superuser Fixture ---
@pytest.fixture(scope="function")
def superuser(db):
    """
    Create a superuser directly in the test database without calling the API.
    """
    user = User(
        email="admin@test.com",
        full_name="Admin User",
        hashed_password=get_password_hash("AdminPass123!"),
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"user_id": user.id})
    return {"id": user.id, "email": user.email, "token": token}


# --- Helper to create normal users ---
def create_user(client, token, email, full_name, password="SecurePass123!"):
    user_data = {
        "email": email,
        "full_name": full_name,
        "password": password,
        "is_superuser": False,
    }
    resp = client.post(
        "/api/users/", json=user_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 201
    return resp.json()

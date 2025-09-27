# backend/app/main.py

from fastapi import FastAPI

from app.api.api import api_router
from app.db.base import Base, engine, SessionLocal
# Import all models to ensure they are registered with SQLAlchemy's Base
from app.models.user import User
from app.models.task import Task
# from app.models.project import Project (will be added later)

# Create the database tables
# This is a development-only step. In production, we will use Alembic migrations.

app = FastAPI(
    title="Task Manager API",
    description="A simple and intuitive task manager with user and project management.",
    version="0.1.1",
)

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include the main API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Manager API!"}
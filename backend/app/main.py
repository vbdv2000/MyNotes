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
    description="""
    A simple and intuitive task manager with user and project management.
    
    ## Features
    
    * 👥 **User Management**: Registration, authentication, and role-based access control
    * 📁 **Projects**: Create and manage projects with multiple collaborators
    * ✅ **Tasks**: Organize work with assignable tasks within projects
    * 🤝 **Collaboration**: Work together with team members on projects
    
    ## Authentication
    
    All API endpoints (except registration and login) require Bearer token authentication.
    To get a token:
    1. Register a new user at `/api/users/`
    2. Login at `/api/auth/login` to get your token
    3. Include the token in all requests using the Authorization header:
       `Authorization: Bearer your_token_here`
    """,
    version="0.1.1",
    contact={
        "name": "Development Team",
        "email": "support@taskmanager.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication operations. Use these endpoints to login and manage access tokens.",
        },
        {
            "name": "users",
            "description": "User management operations. Create, update, and manage user accounts.",
        },
        {
            "name": "projects",
            "description": "Project operations. Create and manage projects, add collaborators.",
        },
        {
            "name": "tasks",
            "description": "Task operations. Create, update, and manage tasks within projects.",
        },
    ],
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

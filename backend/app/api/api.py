from fastapi import APIRouter

from app.api.endpoints import users, projects, auth, notifications, tags, tasks

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/projects", tags=["tasks"])
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["notifications"]
)
api_router.include_router(
    tags.router,
    prefix="/projects/{project_id}",
    tags=["tags"],
)

# app/core/config.py
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mi_super_secreto_para_proyecto")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24


def get_cors_origins():
    origins = os.getenv("BACKEND_CORS_ORIGINS", "")
    return [o.strip() for o in origins.split(",") if o.strip()]


CORS_ORIGINS = get_cors_origins()

settings = Settings()

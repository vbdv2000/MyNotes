# app/core/config.py
from pydantic_settings import BaseSettings
import os
class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mi_super_secreto_para_proyecto")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

settings = Settings()

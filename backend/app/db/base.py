from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker

# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

# Build the database URL from environment variables
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('DB_HOST', 'db')}:5432/{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@as_declarative()
class Base:
    """Base class which provides automated table name
    and primary key generation."""
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Any
    __name__: str

def get_db():
    """
    Returns a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

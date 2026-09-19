"""
Database connection setup using SQLAlchemy.

This module creates:
- `engine`   -> the object that manages the actual connection to PostgreSQL
- `SessionLocal` -> a factory that creates new database sessions
- `Base`     -> the base class that all ORM models (tables) inherit from
- `get_db`   -> a FastAPI dependency that provides a database session
                 to each request and closes it afterwards
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency. Yields a database session for a single request
    and guarantees it is closed afterwards, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

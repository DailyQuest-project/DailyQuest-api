"""Database configuration and connection management for DailyQuest API.

This module provides database connection setup, session management,
and utility functions for database operations using SQLAlchemy.
"""

import os
import time
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import OperationalError

from src.config import DATABASE_URL

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost/dailyquest"
)

engine = create_engine(DATABASE_URL)

SESSIONLOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def wait_for_db(max_retries: int = 30, delay: float = 1) -> bool:
    """Wait for database to be ready with retry mechanism"""
    for attempt in range(max_retries):
        try:
            with engine.connect():
                return True
        except OperationalError:
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                raise
    return False


def create_tables() -> None:
    """Create database tables"""
    # pylint: disable=import-outside-toplevel,unused-import
    from src.users.model import User
    from src.task.model import Habit, ToDo
    from src.tags.model import Tag
    from src.task_completions.model import TaskCompletion
    from src.achievements.model import Achievement, UserAchievement

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session with proper cleanup and error handling.

    Yields:
        Session: SQLAlchemy database session

    Raises:
        Exception: If database connection fails
    """
    db = SESSIONLOCAL()
    try:
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

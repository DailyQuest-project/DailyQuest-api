"""User model for authentication and user management in DailyQuest API.

This module defines the User model with authentication fields,
progress tracking (XP, level, coins), and user preferences.
"""

import uuid
from typing import Any

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from ..database import Base


class User(Base):
    """User model for storing user account information and progress.

    Handles user authentication, XP/level progression, coins,
    and user interface preferences like theme and avatar.
    """

    __tablename__ = "users"

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("xp", 0)
        kwargs.setdefault("level", 1)
        kwargs.setdefault("coins", 0)
        kwargs.setdefault("theme", "light")
        super().__init__(**kwargs)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)

    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    coins = Column(Integer, default=0)

    avatar_url = Column(String, nullable=True)
    theme = Column(String, default="light")

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional, Any
import uuid

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v

    @field_validator("password")
    @classmethod
    def password_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Password cannot be empty")
        return v


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    username: str
    email: EmailStr
    xp: int
    level: int
    coins: int
    avatar_url: Optional[str] = None
    theme: str

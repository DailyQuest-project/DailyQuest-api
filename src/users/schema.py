from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

# Schemas Pydantic para validação e serialização de dados
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class User(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    xp: int
    level: int
    coins: int
    avatar_url: Optional[str] = None
    theme: str

    class Config:
        from_attributes = True
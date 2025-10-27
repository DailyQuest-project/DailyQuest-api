from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from uuid import UUID


class TagBase(BaseModel):
    name: str
    color: Optional[str] = None


class TagCreate(TagBase):
    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v


class TagResponse(TagBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

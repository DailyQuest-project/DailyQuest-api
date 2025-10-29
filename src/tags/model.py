"""Tag model for task organization in DailyQuest API.

This module defines the Tag model and its relationship with tasks
for categorizing and organizing user tasks.
"""
import uuid
from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base

task_tag_association = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", UUID(as_uuid=True), ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    """Tag model for categorizing and organizing tasks.
    
    Tags allow users to organize their tasks by categories, projects,
    or any custom classification system they prefer.
    """
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    color = Column(String, nullable=True)

    tasks = relationship("Task", secondary=task_tag_association, back_populates="tags")

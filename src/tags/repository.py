"""Tag repository for database operations in DailyQuest API.

This module provides repository pattern implementation for tag-related
database operations including CRUD functionality.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from .model import Tag
from .schema import TagCreate, TagUpdate


class TagRepository:
    """Repository class for tag database operations.

    Provides methods for creating, reading, updating, and deleting
    tags with proper user isolation.
    """

    def create_tag(self, db: Session, tag: TagCreate, user_id: UUID) -> Tag:
        """Criar uma nova tag"""
        db_tag = Tag(name=tag.name, color=tag.color, user_id=user_id)
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag

    def get_tags_by_user(self, db: Session, user_id: UUID) -> List[Tag]:
        """Buscar todas as tags de um usuário"""
        return db.query(Tag).filter(Tag.user_id == user_id).all()

    def get_tag_by_id(self, db: Session, tag_id: UUID, user_id: UUID) -> Optional[Tag]:
        """Buscar uma tag específica por ID e usuário"""
        return db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user_id).first()

    def update_tag(
        self, db: Session, tag_id: UUID, user_id: UUID, tag_update: TagUpdate
    ) -> Optional[Tag]:
        """Atualizar uma tag existente"""
        db_tag = self.get_tag_by_id(db, tag_id, user_id)

        if db_tag:
            if tag_update.name is not None:
                db_tag.name = tag_update.name
            if tag_update.color is not None:
                db_tag.color = tag_update.color

            db.commit()
            db.refresh(db_tag)

        return db_tag

    def delete_tag(self, db: Session, tag_id: UUID, user_id: UUID) -> bool:
        """Deletar uma tag"""
        db_tag = self.get_tag_by_id(db, tag_id, user_id)

        if db_tag:
            db.delete(db_tag)
            db.commit()
            return True

        return False

from sqlalchemy.orm import Session
from . import model, schema
from ..utils import hash_password

# Lógica de acesso a dados

class UserRepository:
    def get_user_by_email(self, db: Session, email: str):
        return db.query(model.User).filter(model.User.email == email).first()
    def get_user_by_username(self, db: Session, username: str):
        return db.query(model.User).filter(model.User.username == username).first()
    def create_user(self, db: Session, user: schema.UserCreate):
        hashed_pass = hash_password(user.password)
        
        db_user = model.User(
            username=user.username,
            email=user.email,
            password_hash=hashed_pass
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
import uuid
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID 
from ..database import Base


# Modelo SQLAlchemy da tabela users
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) 
    username = Column(String, unique=True, index=True, nullable=False)
    
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    coins = Column(Integer, default=0)
    
    avatar_url = Column(String, nullable=True)
    theme = Column(String, default='light')
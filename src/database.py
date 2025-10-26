# Conexão SQLAlchemy e sessões
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
from .config import settings
import time

# Usa a URL do arquivo de configuração
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def wait_for_db(max_retries: int = 30, delay: float = 1):
    """Wait for database to be ready with retry mechanism"""
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                return True
        except OperationalError:
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                raise
    return False

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
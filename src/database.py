# Conexão SQLAlchemy e sessões
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import OperationalError
import time
from typing import Generator
from src.config import DATABASE_URL

# Configuração do banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost/dailyquest"
)

# Criação do engine
engine = create_engine(DATABASE_URL)

# Criação da sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()


def wait_for_db(max_retries: int = 30, delay: float = 1) -> bool:
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


def create_tables() -> None:
    """Create database tables"""
    Base.metadata.create_all(bind=engine)


# Função para obter a sessão do banco
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        # Testar a conexão
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

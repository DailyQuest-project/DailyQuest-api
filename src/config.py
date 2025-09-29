from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://dailyquest:dev123@db:5432/dailyquest_db")
    
    class Config:
        env_file = ".env"

settings = Settings()
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://dailyquest:dev123@db:5432/dailyquest_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "7NDRuYThWQw2xrJam1EVO4Y4F2L6mZ6G")
    JWT_ALGORITHM: str = "HS512"
    
    class Config:
        env_file = ".env"

settings = Settings()
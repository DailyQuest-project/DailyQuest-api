from fastapi import FastAPI
from src.users import router as user_router
from .auth.router import router as auth_router
from src.database import wait_for_db, create_tables
from src.users import model as user_model

tags_metadata = [
    {
        "name": "Users",  
        "description": "Operações com usuários, como criação, login e gerenciamento.",
    },
]

app = FastAPI(
    title="DailyQuest API",
    description="API para o aplicativo DailyQuest.",
    version="0.1.0",
    openapi_tags=tags_metadata 
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    wait_for_db()
    create_tables()

app.include_router(user_router.router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "DailyQuest API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
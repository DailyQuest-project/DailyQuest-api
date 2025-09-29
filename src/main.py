from fastapi import FastAPI
from src.users import router as user_router
from src.config import settings
from src.database import engine, Base
from src.users import model as user_model  

Base.metadata.create_all(bind=engine)

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


app.include_router(user_router.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "DailyQuest API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
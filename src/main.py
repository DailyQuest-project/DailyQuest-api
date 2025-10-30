"""Main application module for DailyQuest API.

This module contains the FastAPI application setup, router configuration,
and application lifecycle management.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database import create_tables, wait_for_db
from src.users.router import router as users_router
from src.task.router import router as tasks_router
from src.tags.router import router as tags_router
from src.task_completions.router import router as task_completions_router
from src.achievements.router import router as achievements_router
from src.dashboard.router import router as dashboard_router
from .seed import seed_database

tags_metadata = [
    {
        "name": "Users",
        "description": "Operações com usuários, como criação, login e gerenciamento.",
    },
    {
        "name": "Tasks",
        "description": "Operações com tarefas, hábitos e todos.",
    },
    {
        "name": "Task Completions",
        "description": "Operações de check-in e completar tarefas.",
    },
    {
        "name": "Tags",
        "description": "Operações com tags para organizar tarefas.",
    },
    {
        "name": "Dashboard & History",
        "description": "Analytics, histórico e estatísticas do usuário.",
    },
    {
        "name": "Achievements",
        "description": "Sistema de conquistas e badges do usuário.",
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    print("API iniciando... Aguardando banco de dados...")
    wait_for_db()
    print("Criando tabelas...")
    create_tables()
    print("Rodando o seed do banco de dados...")
    seed_database()
    print("Seeding concluído (ou dados já existiam). API pronta.")
    yield
    print("API desligando...")


app = FastAPI(
    title="DailyQuest API",
    description="API para o aplicativo DailyQuest.",
    version="0.1.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.include_router(users_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(task_completions_router, prefix="/api/v1")
app.include_router(tags_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(achievements_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint that returns API status."""
    return {"message": "DailyQuest API is running!"}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring API availability."""
    return {"status": "healthy"}

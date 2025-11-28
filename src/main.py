"""Main application module for DailyQuest API.

This module contains the FastAPI application setup, router configuration,
and application lifecycle management.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import create_tables, wait_for_db
from src.users.router import router as users_router
from src.task.router import router as tasks_router
from src.tags.router import router as tags_router
from src.task_completions.router import router as task_completions_router
from src.achievements.router import router as achievements_router
from src.dashboard.router import router as dashboard_router
from src.seed import seed_database
from src.config import TESTING

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
    logger = logging.getLogger(__name__)

    logger.info("API iniciando... Aguardando banco de dados...")
    wait_for_db()
    logger.info("Criando tabelas...")
    create_tables()

    # Só executa o seed se não estiver em modo de teste
    if not TESTING:
        logger.info("Rodando o seed do banco de dados...")
        seed_database()
        logger.info("Seeding concluído (ou dados já existiam). API pronta.")
    else:
        logger.info("Modo de teste detectado - seed desabilitado. API pronta.")

    yield
    logger.info("API desligando...")


app = FastAPI(
    title="DailyQuest API",
    description="API para o aplicativo DailyQuest.",
    version="0.1.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# Configuração de CORS para permitir requisições do frontend
allowed_origins = [
    "http://localhost:3000",
    "http://frontend:3000",
    "http://127.0.0.1:3000",
]

# Adicionar origem do Vercel em produção
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    allowed_origins.extend([
        f"https://{vercel_url}",
        "https://*.vercel.app",
    ])

# Adicionar domínio personalizado se existir
custom_domain = os.getenv("FRONTEND_URL")
if custom_domain:
    allowed_origins.append(custom_domain)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

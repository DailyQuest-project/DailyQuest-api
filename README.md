# DailyQuest API

Backend FastAPI com PostgreSQL, SQLAlchemy e Alembic.

## Tecnologias

- FastAPI, SQLAlchemy, Alembic
- PostgreSQL 15, Pydantic
- Pytest, Pylint, Mypy

## Usuários de Teste

| Usuário | Email | Senha | Descrição |
|---------|-------|-------|-----------|
| `testuser` | test@example.com | `testpass123` | Usuário básico |
| `demo` | demo@dailyquest.com | `demo123` | Usuário avançado (Nível 8) |

## Quick Start

```bash
# Com Docker
docker compose up --build

# API disponível em: http://localhost:8000
# Docs Swagger: http://localhost:8000/docs
```

## Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/tasks` | Listar tarefas |
| POST | `/api/v1/tasks` | Criar tarefa |
| POST | `/api/v1/tasks/{id}/complete` | Completar tarefa |
| GET | `/api/v1/dashboard/stats` | Estatísticas |
| GET | `/api/v1/achievements` | Conquistas |

## Testes e Qualidade

```bash
# Testes com coverage
docker compose exec backend pytest --cov=src --cov-report=html:htmlcov --cov-report=term-missing

# Apenas testes
docker compose exec backend pytest --cov=src --cov-report=term-missing

# Linter
docker compose exec backend pylint src/
```

## Migrations

```bash
# Criar migration
docker compose exec backend alembic revision --autogenerate -m "descrição"

# Aplicar migrations
docker compose exec backend alembic upgrade head
```

## Estrutura

```
src/
├── config.py          # Configurações
├── database.py        # Conexão DB
├── security.py        # Auth/JWT
├── seed.py            # Dados iniciais
├── users/             # Módulo usuários
├── task/              # Hábitos e ToDos
├── achievements/      # Sistema conquistas
├── dashboard/         # Analytics
└── tags/              # Tags/categorias
```

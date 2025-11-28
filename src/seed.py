"""Database seeding module for DailyQuest API.

This module provides functionality to seed the database with initial data,
particularly achievements data and test users required for the application to function.
"""

import sys
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL
from src.achievements.model import Achievement, AchievementKey, UserAchievement
from src.users.model import User
from src.security import hash_password
from src.tags.model import Tag
from src.task.model import Habit, ToDo, Difficulty, HabitFrequencyType
from src.task_completions.model import TaskCompletion

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

engine = create_engine(DATABASE_URL)
SESSIONLOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ACHIEVEMENTS_TO_SEED: List[Dict[str, Any]] = [
    # Progressão de Nível
    {
        "name": "Nível 5",
        "description": "Alcance o Nível 5.",
        "icon": "🏆",
        "category": "Progressão",
        "requirement_key": AchievementKey.LEVEL_5,
    },
    {
        "name": "Nível 10",
        "description": "Alcance o Nível 10.",
        "icon": "⭐",
        "category": "Progressão",
        "requirement_key": AchievementKey.LEVEL_10,
    },
    {
        "name": "Veterano",
        "description": "Alcance o Nível 20.",
        "icon": "💎",
        "category": "Progressão",
        "requirement_key": AchievementKey.LEVEL_20,
    },
    {
        "name": "Lendário",
        "description": "Alcance o Nível 50.",
        "icon": "👑",
        "category": "Progressão",
        "requirement_key": AchievementKey.LEVEL_50,
    },

    # Primeiros Passos
    {
        "name": "Bem-vindo!",
        "description": "Faça seu primeiro login.",
        "icon": "👋",
        "category": "Primeiros Passos",
        "requirement_key": AchievementKey.FIRST_LOGIN,
    },
    {
        "name": "Criador de Hábitos",
        "description": "Complete um hábito pela primeira vez.",
        "icon": "🎯",
        "category": "Primeiros Passos",
        "requirement_key": AchievementKey.FIRST_HABIT,
    },
    {
        "name": "Primeira Tarefa",
        "description": "Complete um ToDo pela primeira vez.",
        "icon": "✅",
        "category": "Primeiros Passos",
        "requirement_key": AchievementKey.FIRST_TODO,
    },
    {
        "name": "Organizador",
        "description": "Crie 5 hábitos diferentes.",
        "icon": "📋",
        "category": "Primeiros Passos",
        "requirement_key": AchievementKey.CREATE_5_HABITS,
    },

    # Streaks
    {
        "name": "Em Chamas!",
        "description": "Alcance uma sequência de 3 dias em qualquer hábito.",
        "icon": "🔥",
        "category": "Streaks",
        "requirement_key": AchievementKey.STREAK_3,
    },
    {
        "name": "Implacável",
        "description": "Alcance uma sequência de 7 dias em qualquer hábito.",
        "icon": "🚀",
        "category": "Streaks",
        "requirement_key": AchievementKey.STREAK_7,
    },
    {
        "name": "Mestre da Consistência",
        "description": "Alcance uma sequência de 30 dias em qualquer hábito.",
        "icon": "⚡",
        "category": "Streaks",
        "requirement_key": AchievementKey.STREAK_30,
    },
    {
        "name": "Inabalável",
        "description": "Alcance uma sequência de 100 dias em qualquer hábito.",
        "icon": "💪",
        "category": "Streaks",
        "requirement_key": AchievementKey.STREAK_100,
    },

    # Produtividade
    {
        "name": "Começando Bem",
        "description": "Complete 10 tarefas no total.",
        "icon": "🌱",
        "category": "Produtividade",
        "requirement_key": AchievementKey.COMPLETE_10_TASKS,
    },
    {
        "name": "Produtivo",
        "description": "Complete 50 tarefas no total.",
        "icon": "🌿",
        "category": "Produtividade",
        "requirement_key": AchievementKey.COMPLETE_50_TASKS,
    },
    {
        "name": "Máquina de Tarefas",
        "description": "Complete 100 tarefas no total.",
        "icon": "🌳",
        "category": "Produtividade",
        "requirement_key": AchievementKey.COMPLETE_100_TASKS,
    },
    {
        "name": "Mestre da Produtividade",
        "description": "Complete 500 tarefas no total.",
        "icon": "🏅",
        "category": "Produtividade",
        "requirement_key": AchievementKey.COMPLETE_500_TASKS,
    },

    # Especiais
    {
        "name": "Semana Perfeita",
        "description": "Complete todas as suas tarefas por 7 dias seguidos.",
        "icon": "💯",
        "category": "Especiais",
        "requirement_key": AchievementKey.PERFECT_WEEK,
    },
    {
        "name": "Madrugador",
        "description": "Complete uma tarefa antes das 8h da manhã.",
        "icon": "🌅",
        "category": "Especiais",
        "requirement_key": AchievementKey.EARLY_BIRD,
    },
    {
        "name": "Coruja Noturna",
        "description": "Complete uma tarefa depois das 22h.",
        "icon": "🦉",
        "category": "Especiais",
        "requirement_key": AchievementKey.NIGHT_OWL,
    },
]


def create_initial_tags(db, user_id) -> List[Tag]:
    """Create initial tags for a new user.

    Returns the list of created tags.
    """
    initial_tags_data = [
        {"name": "Saúde", "color": "#4CAF50"},  # Verde
        {"name": "Estudo", "color": "#2196F3"},  # Azul
        {"name": "Trabalho", "color": "#FF9800"},  # Laranja
        {"name": "Exercício", "color": "#F44336"},  # Vermelho
        {"name": "Bem-estar", "color": "#9C27B0"},  # Roxo
        {"name": "Produtividade", "color": "#00BCD4"},  # Ciano
    ]

    created_tags = []
    for tag_data in initial_tags_data:
        tag = Tag(
            user_id=user_id,
            name=tag_data["name"],
            color=tag_data["color"]
        )
        db.add(tag)
        created_tags.append(tag)

    db.flush()  # Para garantir que os IDs sejam gerados
    return created_tags


def create_default_habit(db, user_id, health_tag_id=None) -> None:
    """Create a default 'Drink Water' habit for new users."""

    default_habit = Habit(
        title="💧 Beber 2L de Água",
        description=(
            "Manter-se hidratado é essencial para a saúde. "
            "Beba pelo menos 2 litros de água por dia!"
        ),
        user_id=user_id,
        difficulty=Difficulty.EASY,
        frequency_type=HabitFrequencyType.DAILY,
        is_active=True,
        current_streak=0
    )

    db.add(default_habit)
    db.flush()  # Para gerar o ID do hábito

    # Se tiver a tag de Saúde, associar ao hábito
    if health_tag_id:
        db.execute(
            text(
                "INSERT INTO task_tags (task_id, tag_id) VALUES (:task_id, :tag_id)"
            ),
            {"task_id": default_habit.id, "tag_id": health_tag_id}
        )

    print(f"  ✅ Hábito padrão criado: {default_habit.title}")


def seed_test_user(db) -> None:
    """Create a test user for development and testing purposes.

    Creates a test user with known credentials that can be used in tests.
    This function is idempotent - it can be safely run multiple times.
    """
    # Verificar se o usuário de teste já existe
    existing_user = db.query(User).filter(User.username == "testuser").first()

    if not existing_user:
        print("  Criando usuário de teste...")
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("testpass123"),
            xp=0,
            level=1,
            coins=0,
            theme="light",
        )
        db.add(test_user)
        db.flush()  # Para gerar o ID do usuário

        # Criar tags iniciais para o usuário de teste
        print("  Criando tags iniciais...")
        tags = create_initial_tags(db, test_user.id)

        # Pegar a tag "Saúde" para associar ao hábito padrão
        health_tag = next((tag for tag in tags if tag.name == "Saúde"), None)

        # Criar hábito padrão
        print("  Criando hábito padrão...")
        create_default_habit(db, test_user.id, health_tag.id if health_tag else None)

        db.commit()
        print("  ✅ Usuário de teste criado: testuser")
        print(f"  ✅ Tags criadas: {len(tags)}")
    else:
        print("  ℹ️  Usuário de teste já existe: testuser")


def seed_advanced_test_user(db) -> None:  # pylint: disable=too-many-locals,too-many-statements
    """Create an advanced test user with 15 days of history and achievements.

    This creates a demo user with:
    - 15 days of completion history
    - Multiple habits and todos
    - Several unlocked achievements
    - XP and level progression
    """
    # Verificar se o usuário já existe
    existing_user = db.query(User).filter(User.username == "demo").first()

    if existing_user:
        print("  ℹ️  Usuário demo já existe, removendo para recriar...")
        # Remover dados relacionados primeiro
        uid = existing_user.id
        db.execute(
            text("DELETE FROM task_completions WHERE user_id = :uid"),
            {"uid": uid}
        )
        db.execute(
            text("DELETE FROM user_achievements WHERE user_id = :uid"),
            {"uid": uid}
        )
        db.execute(
            text(
                "DELETE FROM task_tags WHERE task_id IN "
                "(SELECT id FROM tasks WHERE user_id = :uid)"
            ),
            {"uid": uid}
        )
        db.execute(text("DELETE FROM tasks WHERE user_id = :uid"), {"uid": uid})
        db.execute(text("DELETE FROM tags WHERE user_id = :uid"), {"uid": uid})
        db.delete(existing_user)
        db.commit()

    print("  🎮 Criando usuário demo avançado...")

    # Calcular XP total para 15 dias de atividade
    # ~150 XP por dia (3 hábitos easy=10xp + 2 todos medium=20xp = 70xp, com bônus de streak)
    total_xp = 2500  # Aproximadamente nível 8-9
    level = 8

    demo_user = User(
        username="demo",
        email="demo@dailyquest.com",
        password_hash=hash_password("demo123"),
        xp=total_xp,
        level=level,
        coins=750,  # Moedas acumuladas
        theme="dark",
    )
    db.add(demo_user)
    db.flush()

    print(f"  ✅ Usuário demo criado: demo (Nível {level}, {total_xp} XP)")

    # Criar tags
    tags_data = [
        {"name": "Saúde", "color": "#4CAF50"},
        {"name": "Estudo", "color": "#2196F3"},
        {"name": "Trabalho", "color": "#FF9800"},
        {"name": "Exercício", "color": "#F44336"},
        {"name": "Bem-estar", "color": "#9C27B0"},
    ]

    created_tags = {}
    for tag_data in tags_data:
        tag = Tag(user_id=demo_user.id, name=tag_data["name"], color=tag_data["color"])
        db.add(tag)
        db.flush()
        created_tags[tag_data["name"]] = tag

    print(f"  ✅ Tags criadas: {len(created_tags)}")

    # Criar hábitos
    habits_data = [
        {
            "title": "💧 Beber 2L de Água",
            "description": "Manter hidratação diária",
            "difficulty": Difficulty.EASY,
            "tag": "Saúde"
        },
        {
            "title": "📚 Estudar 1 hora",
            "description": "Manter consistência nos estudos",
            "difficulty": Difficulty.MEDIUM,
            "tag": "Estudo"
        },
        {
            "title": "🏃 Exercício físico",
            "description": "30 min de atividade física",
            "difficulty": Difficulty.HARD,
            "tag": "Exercício"
        },
        {
            "title": "🧘 Meditar 10 min",
            "description": "Prática diária de mindfulness",
            "difficulty": Difficulty.EASY,
            "tag": "Bem-estar"
        },
        {
            "title": "📖 Ler 20 páginas",
            "description": "Leitura diária",
            "difficulty": Difficulty.MEDIUM,
            "tag": "Estudo"
        },
    ]

    created_habits = []
    for habit_data in habits_data:
        habit = Habit(
            title=habit_data["title"],
            description=habit_data["description"],
            user_id=demo_user.id,
            difficulty=habit_data["difficulty"],
            frequency_type=HabitFrequencyType.DAILY,
            is_active=True,
            current_streak=15,  # 15 dias de streak
            last_completed=datetime.utcnow(),
        )
        db.add(habit)
        db.flush()

        # Associar tag
        if habit_data["tag"] in created_tags:
            db.execute(
                text(
                    "INSERT INTO task_tags (task_id, tag_id) VALUES (:task_id, :tag_id)"
                ),
                {"task_id": habit.id, "tag_id": created_tags[habit_data["tag"]].id}
            )

        created_habits.append(habit)

    print(f"  ✅ Hábitos criados: {len(created_habits)}")

    # Criar ToDos (alguns completados, alguns pendentes)
    todos_data = [
        {
            "title": "📋 Organizar documentos",
            "description": "Organizar pasta de documentos",
            "difficulty": Difficulty.EASY,
            "completed": True
        },
        {
            "title": "🛒 Fazer compras do mês",
            "description": "Lista de supermercado",
            "difficulty": Difficulty.MEDIUM,
            "completed": True
        },
        {
            "title": "💻 Atualizar portfólio",
            "description": "Adicionar projetos recentes",
            "difficulty": Difficulty.HARD,
            "completed": True
        },
        {
            "title": "📞 Ligar para o médico",
            "description": "Agendar consulta anual",
            "difficulty": Difficulty.EASY,
            "completed": False
        },
        {
            "title": "🎓 Revisar material da prova",
            "description": "Estudar capítulos 5-8",
            "difficulty": Difficulty.MEDIUM,
            "completed": False
        },
    ]

    created_todos = []
    for todo_data in todos_data:
        deadline = datetime.utcnow() + timedelta(days=7) if not todo_data["completed"] else None
        completed_at = datetime.utcnow() - timedelta(days=5) if todo_data["completed"] else None

        todo = ToDo(
            title=todo_data["title"],
            description=todo_data["description"],
            user_id=demo_user.id,
            difficulty=todo_data["difficulty"],
            is_active=True,
            deadline=deadline,
            completed=todo_data["completed"],
            completed_at=completed_at,
        )
        db.add(todo)
        db.flush()
        created_todos.append(todo)

    completed_count = sum(1 for t in todos_data if t['completed'])
    print(f"  ✅ ToDos criados: {len(created_todos)} ({completed_count} completados)")

    # Criar histórico de completions (15 dias + hoje)
    xp_values = {"EASY": 10, "MEDIUM": 20, "HARD": 30}
    completion_count = 0

    # Incluir hoje (0) até 15 dias atrás
    for days_ago in range(15, -1, -1):  # 15, 14, 13... 1, 0 (hoje)
        completion_date = datetime.utcnow() - timedelta(days=days_ago)

        # Completar todos os hábitos para cada dia
        for habit in created_habits:
            xp_earned = xp_values.get(habit.difficulty.value, 10)

            completion = TaskCompletion(
                task_id=habit.id,
                user_id=demo_user.id,
                completed_date=completion_date,
                xp_earned=xp_earned,
            )
            db.add(completion)
            completion_count += 1

    # Adicionar completions para os ToDos completados
    for todo in created_todos:
        if todo.completed:
            xp_earned = xp_values.get(todo.difficulty.value, 10)
            completion = TaskCompletion(
                task_id=todo.id,
                user_id=demo_user.id,
                completed_date=todo.completed_at,
                xp_earned=xp_earned,
            )
            db.add(completion)
            completion_count += 1

    print(f"  ✅ Histórico de completions: {completion_count} registros")

    # Desbloquear conquistas
    achievements_to_unlock = [
        AchievementKey.FIRST_LOGIN,
        AchievementKey.FIRST_HABIT,
        AchievementKey.FIRST_TODO,
        AchievementKey.CREATE_5_HABITS,
        AchievementKey.STREAK_3,
        AchievementKey.STREAK_7,
        AchievementKey.LEVEL_5,
        AchievementKey.COMPLETE_10_TASKS,
        AchievementKey.COMPLETE_50_TASKS,
        AchievementKey.PERFECT_WEEK,
    ]

    unlocked_count = 0
    for ach_key in achievements_to_unlock:
        achievement = db.query(Achievement).filter(Achievement.requirement_key == ach_key).first()
        if achievement:
            user_achievement = UserAchievement(
                user_id=demo_user.id,
                achievement_id=achievement.id,
                unlocked_at=datetime.utcnow() - timedelta(days=unlocked_count),  # Datas variadas
            )
            db.add(user_achievement)
            unlocked_count += 1

    print(f"  ✅ Conquistas desbloqueadas: {unlocked_count}")

    db.commit()
    print("  🎉 Usuário demo criado com sucesso!")
    print("     Login: demo / demo123")
    print(f"     Nível: {level} | XP: {total_xp} | Moedas: 750")
    print(f"     Streak: 15 dias | Conquistas: {unlocked_count}")


def seed_database() -> None:
    """Seed the database with initial data.

    Creates default achievements and test users in the database if they don't already exist.
    This function is idempotent - it can be safely run multiple times.
    """
    print(" Iniciando o seeding do banco de dados...")
    db = SESSIONLOCAL()

    try:
        # Seed achievements
        for ach_data in ACHIEVEMENTS_TO_SEED:
            exists = (
                db.query(Achievement)
                .filter(Achievement.requirement_key == ach_data["requirement_key"])
                .count()
                > 0
            )

            if not exists:
                new_ach = Achievement(**ach_data)
                db.add(new_ach)
                print(f"  Criando conquista: {ach_data['name']} {ach_data['icon']}")
            else:
                print(f"  Conquista já existe: {ach_data['name']}")

        # Seed test user
        seed_test_user(db)

        # Seed advanced demo user with 15 days history
        seed_advanced_test_user(db)

        db.commit()
        print(" Seeding concluído com sucesso!")
        print(f" Total de conquistas no banco: {db.query(Achievement).count()}")
        print(f" Total de usuários no banco: {db.query(User).count()}")
    except Exception as e:
        print(f" Erro durante o seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

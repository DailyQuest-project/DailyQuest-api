# DailyQuest-api

##  Relatórios


docker compose exec backend pytest --cov=src --cov-report=html:htmlcov --cov-report=term-missing --cov-report=xml

docker compose exec backend pytest --cov=src --cov-report=term-missing

docker compose exec backend pylint src/

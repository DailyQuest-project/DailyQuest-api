 # Visão Geral da Suíte de Testes

 Este documento lista os módulos de teste do projeto e uma breve descrição do que cada arquivo de teste cobre. 

 > Resumo da execução de testes (do último run via Docker):
 > - 125 testes passaram
 > - Cobertura total: ~94%
 > - Relatório HTML de cobertura: `htmlcov/`

 ---

 ## src/achievements

 - `achievements/achievements_test.py`
   - Testes unitários e de integração para conquistas (achievements).
   - Cobre: busca de conquista por chave, desbloqueio de conquista para um usuário e comportamento do endpoint `/api/v1/achievements/me`.
   - Inclui testes parametrizados para conquistas acionadas por limiares de nível.

 ## src/auth

 - `auth/test_auth.py`
   - Testes de integração para endpoints de autenticação e manipulação de tokens.
   - Cobre: login com sucesso, username/senha inválidos, credenciais ausentes, cenários parametrizados de login, acesso a endpoints protegidos com token, tokens malformados/inválidos.

 ## src/dashboard

 - `dashboard/test_dashboard.py`
   - Testes unitários para o repositório do dashboard e testes de integração para os endpoints do dashboard.
   - Cobre: recuperação do histórico de completions (vazio e com dados), estatísticas do dashboard (XP total, nível atual, tarefas concluídas, streak atual), proteção de acesso aos endpoints e fluxo ponta a ponta (criar hábito → completar → verificar dashboard e histórico).
   - Testes parametrizados para estatísticas do dashboard com diferentes quantidades de completions.

 ## src/tags

 - `tags/test_tags.py`
   - Testes unitários para o repositório de tags e testes de integração para os endpoints de tags.
   - Cobre: criar/listar/atualizar/deletar tags, comportamento de validação ao criar tags, acesso não autorizado e fluxo completo de CRUD.
   - Testes parametrizados para validação na criação.

 ## src/task

 - `task/test_tasks.py`
   - Testes unitários e de integração para gerenciamento de tarefas (habits e todos).
   - Cobre: helper de conversão para bitmask, criação de hábitos/todos (unit + endpoints), listagem de tarefas, atualização/deleção de hábitos, validação na criação, integração com tags (associar/remover), filtragem por tag, checagens de autorização e fluxos completos.

 - `task/test_task_service.py`
   - Testes de integração para a camada de negócio `TaskService`.
   - Cobre: completar hábitos e todos com interações reais com o banco, atualização de streaks, prevenção de duplicação de completions, lógica de level-up (simples e múltiplo), casos de erro (task/usuário não encontrado), helpers de negócio (`calculate_level_from_xp`, `calculate_xp_needed_for_next_level`) e testes de fluxo abrangentes.

 ## src/task_completions

 - `task_completions/test_task_completions.py`
   - Testes unitários para `TaskCompletionRepository` e testes de integração para endpoints de conclusão de tarefas.
   - Cobre: cálculo de XP por dificuldade (EASY/MEDIUM/HARD), completar hábitos aumenta streaks, completar todos marca como concluído, verificações de endpoints e fluxo de gamificação (acumular XP em múltiplas conclusões), e testes parametrizados para combinações de XP.

 ## src/users

 - `users/test_users.py`
   - Testes unitários e de integração para gerenciamento de usuários e endpoints relacionados.
   - Cobre: valores padrão do modelo User, operações do repositório (criar usuário, buscar por email/username), endpoints para criação de usuários, manejo de email duplicado, proteção de autenticação para `/users/me`, testes de validação e fluxo completo de registro/login/perfil.

 ---

 ## Como executar a suíte de testes

 - Localmente (usando o virtualenv do projeto):

 ```cmd
 venv\\Scripts\\activate
 python -m pip install -r requirements.txt
 python -m pytest --cov=src --cov-report=html --cov-report=term-missing -q
 ```

 - Usando Docker Compose (recomendado — espelha o ambiente do CI):

 ```bash
 docker compose --profile testing up --build --abort-on-container-exit --exit-code-from tests
 ```

 A execução via Docker gera o relatório HTML de cobertura no diretório `htmlcov/`.

 ---

 ## Observações e próximos passos

 - A cobertura está alta (~94%) mas alguns módulos ainda apresentam lacunas relatadas pela ferramenta de coverage (ver `htmlcov/index.html` para detalhes).
 - Se desejar, eu posso:
   - Expandir este documento com links diretos para testes específicos ou asserts importantes.
   - Gerar uma lista curta com as áreas com cobertura faltante (arquivos com < 100% de coverage) e propor testes para adicionar.
   - Abrir um PR com este `TESTS_OVERVIEW.md` e o output da execução de testes embutido.

 ---

 Gerado automaticamente. Se preferir uma estrutura diferente (lista completa por arquivo, agrupamento por unit vs integration, ou inclusão de exemplos diretos de testes), me diga o formato desejado.

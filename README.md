# Universal CRM

Monorepo with FastAPI backend and React frontend.

## Что сделано на Этапе 1
- **Docker Compose**: сервисы `postgres`, `redis`, `minio`, `backend` (FastAPI), `worker` (Celery), `frontend` (Vite/React)
- **Backend foundation (FastAPI + async SQLAlchemy)**:
  - `/health` health-check
  - подключение API роутеров
  - базовые модели/схемы домена: `User`, `Project`, `Task`, `Document`
  - Alembic миграции (включая `User.competency` и `User.load`)

## Что сделано на Этапе 2
- **Новые CRUD-роутеры для `Project` и `Task` в `app/routers/`**:
  - `GET /api/v1/projects`, `POST /api/v1/projects`, `GET /api/v1/projects/{id}`, `PUT /api/v1/projects/{id}`, `DELETE /api/v1/projects/{id}`
  - `GET /api/v1/tasks`, `POST /api/v1/tasks`, `GET /api/v1/tasks/{id}`, `PUT /api/v1/tasks/{id}`, `DELETE /api/v1/tasks/{id}`
  - фильтры задач: `project_id`, `assignee`, `status`
- **CRUD слой**: добавлены `backend/app/crud/projects.py` и `backend/app/crud/tasks.py`
- **Подключение роутеров**: новые `projects/tasks` подключены в `backend/app/main.py` под префиксом `/api/v1`
- **Миграции**: отдельная миграция для Этапа 2 не требовалась (изменений схемы БД нет)
- **Smoke-тест API**: добавлен `backend/scripts/smoke_api_crud.py` для быстрой проверки CRUD-цикла через HTTP API

## Что сделано на Этапе 3
- **AI-автосоздание задач**: добавлен сервис `backend/app/ai/task_auto_creator.py` с классом `TaskAutoCreator` и методом `create_tasks_from_message(...)`.
- **Новый AI-роутер в стиле Stage 2**: добавлен `backend/app/routers/ai.py` и endpoint `POST /api/v1/ai/create-tasks-from-message`.
- **DI для LLM**: добавлены зависимости `get_db` и `get_llm_client` в `backend/app/dependencies.py` (без hardcoded ключей и внешних секретов).
- **Сохранение задач через CRUD**: созданные из сообщения задачи сохраняются через `backend/app/crud/tasks.py`.
- **Smoke-тест AI endpoint**: добавлен `backend/scripts/smoke_ai.py`.

## Что сделано на Этапе 4
- **Реальный LLM-клиент**: добавлен `backend/app/ai/llm_client.py` с `OpenRouterLLMClient` (OpenAI-compatible через `httpx`).
- **DI на реальный LLM**: `backend/app/dependencies.py::get_llm_client()` теперь возвращает `OpenRouterLLMClient` с настройкой из env.
- **OpenClaw webhook**: добавлен `backend/app/routers/openclaw.py` и endpoint `POST /api/v1/openclaw/webhook`.
- **Интеграция webhook -> задачи**: входящее сообщение парсится через `TaskAutoCreator` и сохраняется через CRUD.
- **Smoke-тесты Stage 4**: обновлен `backend/scripts/smoke_ai.py` и добавлен `backend/scripts/smoke_openclaw.py`.

## Quick start
1. Copy `.env.example` to `.env`
2. Run `docker-compose up --build`
3. Open API docs at `http://localhost:8010/docs` (backend mapped to host port **8010** in `docker-compose.yml` to avoid clashing with other stacks on `8000`)

## Запуск (локально, через Docker)
1. Скопируйте переменные окружения: `cp .env.example .env` (на Windows можно просто создать `.env` рядом с `.env.example`).
2. Запустите инфраструктуру и сервисы: `docker-compose up --build`
3. Проверьте health-check: `GET http://localhost:8010/health`
4. Swagger/OpenAPI: `http://localhost:8010/docs`

## Stage 1 DB workflow
1. Start Postgres: `docker-compose up -d postgres`
2. Install backend deps: `pip install -r backend/requirements.txt`
3. Run migration: `cd backend && alembic upgrade head`
4. Run schema smoke: `python backend/scripts/smoke_schema.py`

## Stage 2 API smoke workflow
1. Получите JWT и установите переменную `SMOKE_BEARER_TOKEN`
2. При необходимости задайте `SMOKE_API_BASE_URL` (по умолчанию: `http://localhost:8010/api/v1`)
3. Запустите smoke-тест: `python backend/scripts/smoke_api_crud.py`

## Stage 3 AI endpoint smoke workflow
1. Получите JWT и установите переменную `SMOKE_BEARER_TOKEN`.
2. При необходимости задайте `SMOKE_API_BASE_URL` (по умолчанию: `http://localhost:8010/api/v1`).
3. Запустите AI smoke-тест: `python backend/scripts/smoke_ai.py`.
4. Ручная проверка endpoint:
   - `POST http://localhost:8010/api/v1/ai/create-tasks-from-message`
   - Body:
     ```json
     {
       "message": "- Подготовить отчёт до 15.04.2026; - Согласовать бюджет, ответственный: ivan",
       "project_id": null
     }
     ```

## Stage 4 LLM/OpenClaw setup and smoke
1. В `.env` добавьте:
   - `OPENROUTER_API_KEY=sk-or-...`
   - `OPENROUTER_API_BASE=https://openrouter.ai/api/v1` (по умолчанию)
   - `OPENROUTER_MODEL=anthropic/claude-3.5-sonnet`
   - `OPENROUTER_TIMEOUT_SECONDS=30`
   - `OPENCLAW_API_KEY=<your_webhook_key>`
2. Перезапустите backend: `docker compose up --build -d backend`.
3. Smoke AI (реальный LLM, если `OPENROUTER_API_KEY` есть; иначе fallback): `python backend/scripts/smoke_ai.py`.
4. Smoke webhook: `python backend/scripts/smoke_openclaw.py`.
5. Ручной тест webhook:
   - `POST http://localhost:8010/api/v1/openclaw/webhook`
   - Header: `X-OpenClaw-Api-Key: <OPENCLAW_API_KEY>`
   - Body:
     ```json
     {
       "source": "telegram",
       "message": "Подготовить отчёт до 25.04.2026; исполнитель: ivan",
       "project_id": null
     }
     ```

## Docker troubleshooting
- Compose validates (`docker compose config -q`). If Postgres stays `Created`, check `docker logs crab_assistant-postgres-1` — often **port 5432 already in use** on the host. This project maps Postgres to **host `5433`** (`5433:5432`); from your machine use `DB_HOST=localhost DB_PORT=5433` for tools like `smoke_schema.py` and GUI clients. Services inside Compose still use hostname `postgres` and port `5432`.

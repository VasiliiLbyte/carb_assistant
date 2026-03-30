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

## Docker troubleshooting
- Compose validates (`docker compose config -q`). If Postgres stays `Created`, check `docker logs crab_assistant-postgres-1` — often **port 5432 already in use** on the host. This project maps Postgres to **host `5433`** (`5433:5432`); from your machine use `DB_HOST=localhost DB_PORT=5433` for tools like `smoke_schema.py` and GUI clients. Services inside Compose still use hostname `postgres` and port `5432`.

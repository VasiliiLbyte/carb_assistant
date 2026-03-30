# Universal CRM

Monorepo with FastAPI backend and React frontend.

## Что сделано на Этапе 1
- **Docker Compose**: сервисы `postgres`, `redis`, `minio`, `backend` (FastAPI), `worker` (Celery), `frontend` (Vite/React)
- **Backend foundation (FastAPI + async SQLAlchemy)**:
  - `/health` health-check
  - подключение API роутеров
  - базовые модели/схемы домена: `User`, `Project`, `Task`, `Document`
  - Alembic миграции (включая `User.competency` и `User.load`)

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

## Docker troubleshooting
- Compose validates (`docker compose config -q`). If Postgres stays `Created`, check `docker logs crab_assistant-postgres-1` — often **port 5432 already in use** on the host. This project maps Postgres to **host `5433`** (`5433:5432`); from your machine use `DB_HOST=localhost DB_PORT=5433` for tools like `smoke_schema.py` and GUI clients. Services inside Compose still use hostname `postgres` and port `5432`.

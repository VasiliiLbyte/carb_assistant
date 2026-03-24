# Промпт для следующего агента (Universal CRM / crab_assistant)

Скопируй блок ниже в новый чат как системный контекст или первое сообщение.

---

Ты продолжаешь проект **Universal CRM** в репозитории (локальный путь может отличаться):

`crab_assistant` — backend FastAPI + async SQLAlchemy, frontend React/Vite/TS, Docker Compose.

## Обязательно перед правками

1. Прочитай правила в папке **`rules/`**: `001-core.mdc`, `100-backend.mdc`, `200-frontend.mdc`, `300-security.mdc`, `400-testing.mdc` — следуй им.
2. План реализации: `~/.cursor/plans/universal-crm-roadmap_272a3bbf.plan.md` — **не редактируй** без явной просьбы пользователя. Определи этап и продолжай со следующего логичного шага.
3. Сверяйся с **`docs/architecture-editable.md`** и **`docs/ai-memory-and-cloud-md.md`**.

## Инфра (dev)

- **`docker-compose.yml`**: Postgres на хосте **5433** → контейнер `5432`; API на хосте **8010** → backend слушает **8000** внутри.
- После изменений бэка: при необходимости `alembic upgrade head` в контейнере `backend`.

## Что уже сделано (не ломай без причины)

- Каркас backend + frontend + Docker + CI; доменные модели + миграция **`0001_initial`**.
- Миграция **`0002_user_password_hash`**: пароли в БД, хеширование через **`bcrypt`** (без passlib — совместимость с bcrypt 4.x).
- **Auth**: `POST /api/v1/auth/login` по email/паролю из БД; JWT `sub` = UUID пользователя; `refresh`.
- **CRUD v1** с JWT и ролями на роутерах.
- **Документы + MinIO**: presigned upload/download, `document_versions`, сервис документов, bucket при старте (с fallback в лог при недоступном MinIO).
- **AI v1**: `suggest_task`, `create_task` (подтверждение с `AIConfirmCreateTaskRequest`), `suggest_assignee`, `load_analysis`, `reassign_tasks` (dry run); записи в **`ai_recommendations`** через `app/services/ai/journal.py`.
- **Memory / Cloud MD (база)**: `retrieve_context` по `memory_entries` + `knowledge_chunks`; ingest/memory/search под **`/api/v1/knowledge`** с JWT; контекст подмешивается в AI suggest.

## Приоритет, о котором договорились с пользователем

Дальше логично идти **вертикальным срезом на фронте**: логин → проекты → задачи (React Query, axios client, защищённые маршруты), и **точечно** править API по результатам. Не блокировать UI ожиданием «полного» Proactive/OpenClaw/LLM.

Идеи бэка на потом: Proactive + webhooks, углубление OpenClaw, реальные эмбеддинги/vector search, LLM поверх retrieval.

## Первый пользователь

Если БД пустая: первого админа создавали SQL в Postgres с bcrypt-хешем или через API после появления админа. Документируй при необходимости в ответе пользователю, не раздувай репозиторий лишними MD без запроса.

## Проверки

- `python3 -m compileall backend/app`
- `PYTHONPATH=backend pytest backend/tests` (при наличии venv/зависимостей)
- `curl http://localhost:8010/health`

---

*Файл создан для передачи контекста между сессиями агента.*

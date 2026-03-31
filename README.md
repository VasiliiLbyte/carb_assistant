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

## Что сделано на Этапе 5
- **Document Processor**: добавлен пакет `backend/app/document_processor/` с `DocumentProcessor` и pydantic-схемами.
- **Загрузка и обработка документов**: добавлен роутер `backend/app/routers/documents.py` с endpoint'ами:
  - `POST /api/v1/documents/upload`
  - `POST /api/v1/documents/process`
- **Базовый RAG-пайплайн**: извлечение текста из TXT/PDF/DOCX, вызов OpenRouter LLM, извлечение задач/рисков.
- **Интеграция с CRUD задач**: извлечённые задачи сохраняются через `backend/app/crud/tasks.py`.
- **Smoke-тест Stage 5**: добавлен `backend/scripts/smoke_document.py`.

## Что сделано на Этапе 6
- **Proactive Module**: добавлен пакет `backend/app/proactive/` с `ProactiveEngine`, `RuleEngine` и pydantic-схемами.
- **CRUD правил + триггер пинга**: добавлен роутер `backend/app/routers/proactive.py`:
  - `GET/POST/PUT/DELETE /api/v1/proactive/rules`
  - `POST /api/v1/proactive/trigger`
- **Интеграция с OpenClaw webhook**: `POST /api/v1/openclaw/webhook` теперь поддерживает `message_type=proactive_response` и вызывает обработчик ответов.
- **LLM-генерация сообщений**: для пингов и fallback-интерпретации ответов используется `OpenRouterLLMClient`.
- **Smoke-тест Stage 6**: добавлен `backend/scripts/smoke_proactive.py`.

## Что сделано на Этапе 7
- **Competency & Load Manager + AI Recommender**: добавлен пакет `backend/app/recommender/` с `AIRecommender` и pydantic-схемами.
- **Скоринг исполнителей (top-3)**: учитываются `User.competency`, `User.load`, совпадение навыков (`User.skills`), приоритет задачи и история выполненных похожих задач.
- **LLM-объяснение рекомендации**: используется `OpenRouterLLMClient` через DI для генерации краткого обоснования на русском.
- **Новые API endpoint'ы**: добавлен роутер `backend/app/routers/recommender.py`:
  - `POST /api/v1/recommender/recommend`
  - `POST /api/v1/recommender/apply`
- **Расширение CRUD**:
  - `backend/app/crud/tasks.py::update_assignee(...)` с валидацией роли исполнителя
  - `backend/app/crud/users.py` для обновления `competency` и `load`
- **Smoke-тест Stage 7**: добавлен `backend/scripts/smoke_recommender.py`.

## Что сделано на Этапе 8
- **Risk Analyzer**: добавлен пакет `backend/app/risk_analyzer/` с `RiskAnalyzer` и схемами `RiskCreate`, `RiskOut`, `RiskDetectionRequest`.
- **LLM-детекция рисков из разных источников**:
  - `detect_risks_from_task(task_id)`
  - `detect_risks_from_document(document_key)`
  - `detect_risks_from_message(message, project_id)`
- **Новый API-роутер**: добавлен `backend/app/routers/risks.py`:
  - `GET /api/v1/risks` (фильтр по `project_id`/`task_id`)
  - `POST /api/v1/risks/detect-from-task`
  - `POST /api/v1/risks/detect-from-document`
  - `POST /api/v1/risks/detect-from-message`
- **Приоритизация рисков**: автоматическая классификация severity (`high`/`medium`/`low`) по матрице вероятность x влияние.
- **Интеграция с Proactive**: для `high`-рисков выполняется автоэскалация (`status=escalated`) при наличии включенных proactive-правил с trigger `high_risk_detected`/`high_risk_escalation`.
- **Миграция Stage 8**: `backend/migrations/versions/0004_risk_task_source_severity.py` (добавлены `risks.severity`, `risks.source`, `risks.task_id` + индексы/FK).
- **Smoke-тест Stage 8**: добавлен `backend/scripts/smoke_risk.py`.

## Что сделано на Этапе 9
- **Frontend Dashboard (React 18 + TypeScript + Vite + TailwindCSS)**: обновлена структура `frontend/src` на модульную (`api/`, `hooks/`, `components/`, `pages/`), добавлены переиспользуемые UI-блоки (`ProjectCard`, `TaskList`, `RiskCard`, `RecommendationCard`, `Sidebar`).
- **Главный дашборд**: реализованы секции проектов, задач, рисков и рекомендаций исполнителей; добавлены action-кнопки `Загрузить документ`, `Создать задачу`, `Триггер proactive`.
- **React Query интеграция**: включены hooks `useProjects`, `useTasks`, `useRisks`, `useRecommender` с кэшированием, `staleTime` и автообновлением через `refetchInterval`.
- **API client + JWT-заглушка**: `frontend/src/api/client.ts` использует `axios` с `baseURL` и `Authorization: Bearer <token>` из `localStorage` (`carb_jwt`); добавлена страница `Settings` для сохранения токена.
- **Smoke-тест Stage 9**: добавлен базовый тест `frontend/src/App.smoke.test.tsx` (проверяет, что ключевая навигация рендерится).

## Frontend запуск (Stage 9)
1. Перейдите в каталог фронтенда: `cd frontend`
2. Установите зависимости: `npm install`
3. Запустите dev-сервер: `npm run dev`
4. Откройте дашборд: `http://localhost:5173`

Опционально можно задать API base URL через `VITE_API_BASE_URL` (по умолчанию используется `/api/v1` и проксирование через Vite на `http://localhost:8010`).

## Frontend smoke-проверка
- Запуск тестов: `cd frontend && npm run test`
- Ручная проверка: открыть `http://localhost:5173`, убедиться что видны sidebar и страницы `Dashboard`, `Projects`, `Tasks`, `Documents`, `Risks`, `Settings`.

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

## Stage 5 Document Processor smoke
1. Убедитесь, что backend поднят: `docker compose up --build -d backend`.
2. Установите `SMOKE_BEARER_TOKEN` (JWT с ролью `admin`/`pm`/`engineer`).
3. Запустите тест:
   - из хоста: `python backend/scripts/smoke_document.py`
   - из контейнера: `docker compose exec -e SMOKE_API_BASE_URL=http://127.0.0.1:8000/api/v1 backend python -m scripts.smoke_document`
4. Ручная проверка:
   - `POST /api/v1/documents/upload` (multipart, поле `file`)
   - `POST /api/v1/documents/process` с body `{"file_key":"<from upload>", "project_id": null}`

## Stage 6 Proactive module smoke
1. Убедитесь, что backend поднят: `docker compose up --build -d backend`.
2. Нужны переменные: `SMOKE_BEARER_TOKEN`, `OPENCLAW_API_KEY`.
3. Запустите smoke:
   - из хоста: `python backend/scripts/smoke_proactive.py`
   - из контейнера: `docker compose exec -e SMOKE_API_BASE_URL=http://127.0.0.1:8000/api/v1 backend python -m scripts.smoke_proactive`
4. Пример правила (body для `POST /api/v1/proactive/rules`):
   ```json
   {
     "name": "daily-status-reminder",
     "trigger_type": "daily_status_check",
     "action_type": "send_message",
     "config": {"hour_utc": 9},
     "enabled": true
   }
   ```
5. Пример эскалационного правила:
   ```json
   {
     "name": "escalate-blocked-task",
     "trigger_type": "inprogress_overdue_ping",
     "action_type": "escalate_manager",
     "config": {"days_threshold": 3, "manager_user_id": "<uuid>"},
     "enabled": true
   }
   ```

## Stage 7 Recommender examples and smoke
1. Убедитесь, что backend поднят: `docker compose up --build -d backend`.
2. Установите `SMOKE_BEARER_TOKEN` (JWT с ролью `admin` или `pm`).
3. Запустите smoke:
   - из хоста: `python backend/scripts/smoke_recommender.py`
   - из контейнера: `docker compose exec -e SMOKE_API_BASE_URL=http://127.0.0.1:8000/api/v1 backend python -m scripts.smoke_recommender`
4. Пример рекомендации по существующей задаче:
   - `POST /api/v1/recommender/recommend`
   - body:
   ```json
   {
     "task_id": "<uuid>"
   }
   ```
5. Пример рекомендации по ad-hoc задаче:
   - `POST /api/v1/recommender/recommend`
   - body:
   ```json
   {
     "task": {
       "title": "Подготовить план релиза",
       "description": "Согласовать scope и таймлайн",
       "priority": "high",
       "tags": ["release", "planning"],
       "estimated_hours": 6
     }
   }
   ```
6. Применение рекомендации:
   - `POST /api/v1/recommender/apply`
   - body:
   ```json
   {
     "task_id": "<uuid задачи>",
     "assignee_id": "<uuid исполнителя>"
   }
   ```

## Stage 8 Risk Analyzer examples and smoke
1. Убедитесь, что backend поднят: `docker compose up --build -d backend`.
2. Установите `SMOKE_BEARER_TOKEN` (JWT с ролью `admin`/`pm`/`engineer`).
3. Примените миграции: `cd backend && alembic upgrade head`.
4. Запустите smoke:
   - из хоста: `python backend/scripts/smoke_risk.py`
   - из контейнера: `docker compose exec -e SMOKE_API_BASE_URL=http://127.0.0.1:8000/api/v1 backend python -m scripts.smoke_risk`
5. Примеры ручной проверки:
   - `POST /api/v1/risks/detect-from-task`
   ```json
   {
     "task_id": "<uuid задачи>"
   }
   ```
   - `POST /api/v1/risks/detect-from-document`
   ```json
   {
     "document_key": "projects/<project_uuid>/documents/<file>.txt",
     "project_id": null
   }
   ```
   - `POST /api/v1/risks/detect-from-message`
   ```json
   {
     "message": "Есть риск срыва срока из-за задержки поставщика API",
     "project_id": null
   }
   ```

## Docker troubleshooting
- Compose validates (`docker compose config -q`). If Postgres stays `Created`, check `docker logs crab_assistant-postgres-1` — often **port 5432 already in use** on the host. This project maps Postgres to **host `5433`** (`5433:5432`); from your machine use `DB_HOST=localhost DB_PORT=5433` for tools like `smoke_schema.py` and GUI clients. Services inside Compose still use hostname `postgres` and port `5432`.

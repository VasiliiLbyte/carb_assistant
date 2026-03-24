# Universal CRM Architecture (Editable)

Этот файл предназначен для регулярного редактирования по мере развития проекта.

## High-Level Diagram

```mermaid
flowchart LR
    user[Users]
    web[ReactFrontend]
    api[FastAPIBackend]
    db[(PostgreSQL)]
    redis[(Redis)]
    minio[(MinIO)]
    celery[CeleryWorker]
    openclaw[OpenClaw]
    llm[LLMProviders]
    memory[MemoryBank]
    cloudmd[CloudMDKnowledge]

    user --> web
    web --> api
    api --> db
    api --> redis
    api --> minio
    api --> openclaw
    api --> llm
    api --> memory
    api --> cloudmd

    celery --> redis
    celery --> api
    celery --> openclaw
    celery --> db

    openclaw -->|webhooks| api
```

## Domain Blocks

- `Core CRM`: projects, tasks, users, documents, risks.
- `AI Assistant`: task auto-creator, assignee recommender, load analysis, task updater.
- `Proactive Module`: rule engine, scheduler, response handler.
- `Knowledge Layer`: Memory Bank + Cloud MD with retrieval pipeline.

## Notes For Updates

- Добавляйте новые узлы при расширении интеграций.
- Уточняйте связи в диаграмме перед каждым крупным релизом.
- Сохраняйте этот файл как «источник истины» по архитектуре.

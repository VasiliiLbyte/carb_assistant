import os
from collections.abc import Iterable

from sqlalchemy import create_engine, text


EXPECTED_TABLES: tuple[str, ...] = (
    "users",
    "projects",
    "tasks",
    "documents",
    "document_versions",
    "risks",
    "proactive_rules",
    "message_history",
    "ai_recommendations",
    "memory_entries",
    "knowledge_documents",
    "knowledge_chunks",
)


def _make_sync_url() -> str:
    user = os.getenv("DB_USER", "crm")
    password = os.getenv("DB_PASSWORD", "crm")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "universal_crm")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


def _missing_tables(found: Iterable[str]) -> list[str]:
    found_set = set(found)
    return [table for table in EXPECTED_TABLES if table not in found_set]


def main() -> None:
    engine = create_engine(_make_sync_url())
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
                """
            )
        ).scalars().all()

    missing = _missing_tables(rows)
    if missing:
        raise SystemExit(f"Schema smoke check failed. Missing tables: {', '.join(missing)}")

    print("Schema smoke check passed.")


if __name__ == "__main__":
    main()

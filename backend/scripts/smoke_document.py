"""Smoke test for Stage 5 document upload and processing endpoints."""

from __future__ import annotations

import os

import httpx


def _base_url() -> str:
    return os.getenv("SMOKE_API_BASE_URL", "http://localhost:8010/api/v1").rstrip("/")


def _token() -> str:
    token = os.getenv("SMOKE_BEARER_TOKEN")
    if not token:
        raise SystemExit("SMOKE_BEARER_TOKEN is required for document smoke test")
    return token


def main() -> None:
    headers = {"Authorization": f"Bearer {_token()}"}
    text_content = (
        "Нужно подготовить релизный чеклист до 30.04.2026.\n"
        "Также важно проверить риск просрочки по интеграции платежного шлюза.\n"
    )

    with httpx.Client(timeout=30.0) as client:
        upload_response = client.post(
            f"{_base_url()}/documents/upload",
            headers=headers,
            files={"file": ("smoke_document.txt", text_content.encode("utf-8"), "text/plain")},
            data={"project_id": ""},
        )
        upload_response.raise_for_status()
        upload_data = upload_response.json()
        file_key = upload_data.get("file_key")
        assert isinstance(file_key, str) and file_key

        process_response = client.post(
            f"{_base_url()}/documents/process",
            headers={**headers, "Content-Type": "application/json"},
            json={"file_key": file_key, "project_id": None},
        )
        process_response.raise_for_status()
        process_data = process_response.json()

    assert process_data.get("file_key") == file_key
    tasks = process_data.get("tasks")
    assert isinstance(tasks, list)
    assert len(tasks) >= 1
    assert all("id" in task for task in tasks)
    print("Document processor smoke check passed.")


if __name__ == "__main__":
    main()

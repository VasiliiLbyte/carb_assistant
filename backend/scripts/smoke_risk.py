"""Smoke test for Stage 8 risk analyzer endpoints."""

from __future__ import annotations

import os

import httpx


def _base_url() -> str:
    return os.getenv("SMOKE_API_BASE_URL", "http://localhost:8010/api/v1").rstrip("/")


def _token() -> str:
    token = os.getenv("SMOKE_BEARER_TOKEN")
    if not token:
        raise SystemExit("SMOKE_BEARER_TOKEN is required for risk analyzer smoke test")
    return token


def main() -> None:
    headers = {"Authorization": f"Bearer {_token()}"}
    message_text = (
        "Релиз критично зависит от внешнего API, SLA нестабилен. "
        "Есть риск срыва дедлайна и перерасхода бюджета, нужен mitigation."
    )

    with httpx.Client(timeout=40.0) as client:
        task_resp = client.post(
            f"{_base_url()}/tasks",
            headers=headers,
            json={
                "title": "Risk smoke task",
                "description": "Task used for Stage 8 smoke validation",
                "priority": "high",
                "tags": ["smoke", "risk"],
            },
        )
        task_resp.raise_for_status()
        task_id = task_resp.json()["id"]

        detect_task_resp = client.post(
            f"{_base_url()}/risks/detect-from-task",
            headers=headers,
            json={"task_id": task_id},
        )
        detect_task_resp.raise_for_status()
        detect_task_data = detect_task_resp.json()
        assert isinstance(detect_task_data.get("risks"), list)

        upload_resp = client.post(
            f"{_base_url()}/documents/upload",
            headers=headers,
            files={
                "file": (
                    "risk_smoke.txt",
                    message_text.encode("utf-8"),
                    "text/plain",
                )
            },
            data={"project_id": ""},
        )
        upload_resp.raise_for_status()
        document_key = upload_resp.json()["file_key"]

        detect_document_resp = client.post(
            f"{_base_url()}/risks/detect-from-document",
            headers=headers,
            json={"document_key": document_key, "project_id": None},
        )
        detect_document_resp.raise_for_status()
        detect_document_data = detect_document_resp.json()

        detect_message_resp = client.post(
            f"{_base_url()}/risks/detect-from-message",
            headers=headers,
            json={"message": message_text, "project_id": None},
        )
        detect_message_resp.raise_for_status()
        detect_message_data = detect_message_resp.json()

        list_resp = client.get(f"{_base_url()}/risks", headers=headers)
        list_resp.raise_for_status()
        risks = list_resp.json()

    total_created = (
        int(detect_task_data.get("created_count", 0))
        + int(detect_document_data.get("created_count", 0))
        + int(detect_message_data.get("created_count", 0))
    )
    assert total_created >= 1, "Expected at least one detected risk"
    assert any(item.get("severity") in {"high", "medium", "low"} for item in risks)
    print("Risk analyzer smoke check passed.")


if __name__ == "__main__":
    main()

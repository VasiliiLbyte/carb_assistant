"""Smoke test for Stage 7 recommender module."""

from __future__ import annotations

import os

import httpx


def _base_url() -> str:
    return os.getenv("SMOKE_API_BASE_URL", "http://localhost:8010/api/v1").rstrip("/")


def _token() -> str:
    token = os.getenv("SMOKE_BEARER_TOKEN")
    if not token:
        raise SystemExit("SMOKE_BEARER_TOKEN is required for recommender smoke test")
    return token


def main() -> None:
    headers = {"Authorization": f"Bearer {_token()}"}
    with httpx.Client(timeout=30.0) as client:
        task_resp = client.post(
            f"{_base_url()}/tasks",
            headers=headers,
            json={
                "title": "Recommender smoke task",
                "description": "Task for Stage 7 recommendation flow",
                "priority": "high",
                "tags": ["smoke", "recommendation"],
            },
        )
        task_resp.raise_for_status()
        task_id = task_resp.json()["id"]

        recommend_resp = client.post(
            f"{_base_url()}/recommender/recommend",
            headers=headers,
            json={"task_id": task_id},
        )
        recommend_resp.raise_for_status()
        recommendation = recommend_resp.json()
        candidates = recommendation.get("candidates") or []
        if not candidates:
            raise AssertionError("Expected non-empty candidates list")
        assignee_id = recommendation.get("recommended_user_id")
        if not assignee_id:
            # fallback to first candidate when model returns only candidates
            assignee_id = candidates[0]["user_id"]

        apply_resp = client.post(
            f"{_base_url()}/recommender/apply",
            headers=headers,
            json={"task_id": task_id, "assignee_id": assignee_id},
        )
        apply_resp.raise_for_status()
        apply_payload = apply_resp.json()
        assert apply_payload.get("task_id") == task_id
        assert apply_payload.get("assignee_id") == assignee_id

        task_get_resp = client.get(f"{_base_url()}/tasks/{task_id}", headers=headers)
        task_get_resp.raise_for_status()
        assert task_get_resp.json().get("assignee_id") == assignee_id

    print("Recommender smoke check passed.")


if __name__ == "__main__":
    main()


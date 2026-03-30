"""Smoke test for Stage 6 proactive module."""

from __future__ import annotations

import os

import httpx


def _base_url() -> str:
    return os.getenv("SMOKE_API_BASE_URL", "http://localhost:8010/api/v1").rstrip("/")


def _token() -> str:
    token = os.getenv("SMOKE_BEARER_TOKEN")
    if not token:
        raise SystemExit("SMOKE_BEARER_TOKEN is required for proactive smoke test")
    return token


def _openclaw_key() -> str:
    key = os.getenv("OPENCLAW_API_KEY")
    if not key:
        raise SystemExit("OPENCLAW_API_KEY is required for proactive smoke test")
    return key


def main() -> None:
    headers = {"Authorization": f"Bearer {_token()}"}

    with httpx.Client(timeout=30.0) as client:
        task_resp = client.post(
            f"{_base_url()}/tasks",
            headers=headers,
            json={"title": "Proactive smoke task", "description": "in-progress task", "status": "in-progress"},
        )
        task_resp.raise_for_status()
        task_id = task_resp.json()["id"]

        rule_resp = client.post(
            f"{_base_url()}/proactive/rules",
            headers=headers,
            json={
                "name": "smoke-inprogress-overdue",
                "trigger_type": "inprogress_overdue_ping",
                "action_type": "send_message",
                "config": {"days_threshold": 0},
                "enabled": True,
            },
        )
        rule_resp.raise_for_status()
        rule_id = rule_resp.json()["id"]

        trigger_resp = client.post(
            f"{_base_url()}/proactive/trigger",
            headers=headers,
            json={"rule_id": rule_id, "task_id": task_id},
        )
        trigger_resp.raise_for_status()
        trigger_payload = trigger_resp.json()
        assert trigger_payload.get("sent") is True

        webhook_resp = client.post(
            f"{_base_url()}/openclaw/webhook",
            headers={"X-OpenClaw-Api-Key": _openclaw_key(), "Content-Type": "application/json"},
            json={
                "message": "Задача готово, можно закрывать",
                "source": "telegram",
                "message_type": "proactive_response",
                "user_id": None,
            },
        )
        webhook_resp.raise_for_status()
        webhook_payload = webhook_resp.json()
        proactive_result = webhook_payload.get("proactive_result") or {}
        assert proactive_result.get("processed") is True

        task_get_resp = client.get(f"{_base_url()}/tasks/{task_id}", headers=headers)
        task_get_resp.raise_for_status()
        assert task_get_resp.json().get("status") == "done"

    print("Proactive smoke check passed.")


if __name__ == "__main__":
    main()

"""Smoke test for OpenClaw webhook endpoint."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def _base_url() -> str:
    return os.getenv("SMOKE_API_BASE_URL", "http://localhost:8010/api/v1").rstrip("/")


def _openclaw_key() -> str:
    key = os.getenv("OPENCLAW_API_KEY")
    if not key:
        raise SystemExit("OPENCLAW_API_KEY is required for OpenClaw smoke test")
    return key


def _request(method: str, path: str, payload: dict | None = None) -> tuple[int, dict | None]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(url=f"{_base_url()}{path}", method=method, data=data)
    req.add_header("Accept", "application/json")
    req.add_header("X-OpenClaw-Api-Key", _openclaw_key())
    if payload is not None:
        req.add_header("Content-Type", "application/json")

    try:
        with urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8")
            return response.status, (json.loads(body) if body else None)
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise RuntimeError(f"{method} {path} failed: {exc.code} {body}") from exc


def main() -> None:
    payload = {
        "source": "telegram",
        "message": "- Сверстать лендинг до 20.04.2026; - Проверить аналитику, исполнитель: pavel",
        "project_id": None,
    }
    status_code, response = _request("POST", "/openclaw/webhook", payload)
    assert status_code == 200
    assert response is not None
    assert response.get("accepted") is True
    tasks = response.get("tasks")
    assert isinstance(tasks, list)
    assert len(tasks) >= 1
    assert all("id" in task for task in tasks)
    print("OpenClaw webhook smoke check passed.")


if __name__ == "__main__":
    main()

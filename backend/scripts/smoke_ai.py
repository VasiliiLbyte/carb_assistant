"""Smoke test for Stage 3 AI endpoint."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def _base_url() -> str:
    return os.getenv("SMOKE_API_BASE_URL", "http://localhost:8010/api/v1").rstrip("/")


def _token() -> str:
    token = os.getenv("SMOKE_BEARER_TOKEN")
    if not token:
        raise SystemExit("SMOKE_BEARER_TOKEN is required for AI smoke test")
    return token


def _request(method: str, path: str, payload: dict | None = None) -> tuple[int, dict | None]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(url=f"{_base_url()}{path}", method=method, data=data)
    req.add_header("Authorization", f"Bearer {_token()}")
    req.add_header("Accept", "application/json")
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
    llm_mode = "real OpenRouter LLM" if os.getenv("OPENROUTER_API_KEY") else "fallback parser"
    print(f"Running AI smoke in mode: {llm_mode}")
    payload = {
        "message": "- Подготовить отчёт до 15.04.2026; - Согласовать бюджет, ответственный: ivan",
        "project_id": None,
    }
    status_code, response = _request("POST", "/ai/create-tasks-from-message", payload)
    assert status_code == 201
    assert response is not None
    assert "tasks" in response
    assert isinstance(response["tasks"], list)
    assert len(response["tasks"]) >= 1
    assert all("id" in task for task in response["tasks"])
    print("AI smoke check passed.")


if __name__ == "__main__":
    main()

"""Simple API smoke test for Projects/Tasks CRUD.

Required env:
- SMOKE_BEARER_TOKEN: JWT token with sufficient permissions.

Optional env:
- SMOKE_API_BASE_URL: default "http://localhost:8010/api/v1"
"""

from __future__ import annotations

import json
import os
import uuid
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def _base_url() -> str:
    return os.getenv("SMOKE_API_BASE_URL", "http://localhost:8010/api/v1").rstrip("/")


def _token() -> str:
    token = os.getenv("SMOKE_BEARER_TOKEN")
    if not token:
        raise SystemExit("SMOKE_BEARER_TOKEN is required for API smoke test")
    return token


def _request(method: str, path: str, *, payload: dict | None = None, query: dict | None = None) -> tuple[int, dict | list | None]:
    url = f"{_base_url()}{path}"
    if query:
        url = f"{url}?{urlencode(query)}"

    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = Request(url=url, method=method, data=data)
    request.add_header("Authorization", f"Bearer {_token()}")
    request.add_header("Accept", "application/json")
    if payload is not None:
        request.add_header("Content-Type", "application/json")

    try:
        with urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else None
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise RuntimeError(f"{method} {path} failed: {exc.code} {body}") from exc


def main() -> None:
    run_id = uuid.uuid4().hex[:8]
    project_name = f"smoke-project-{run_id}"
    task_title = f"smoke-task-{run_id}"

    _, created_project = _request(
        "POST",
        "/projects",
        payload={"name": project_name, "project_type": "general", "stage": "planned", "custom_fields": {"smoke": True}},
    )
    project_id = created_project["id"]

    _, project = _request("GET", f"/projects/{project_id}")
    assert project["name"] == project_name

    _, updated_project = _request("PUT", f"/projects/{project_id}", payload={"name": f"{project_name}-updated"})
    assert updated_project["name"].endswith("-updated")

    _, projects = _request("GET", "/projects", query={"limit": 10, "offset": 0})
    assert isinstance(projects, list)

    _, created_task = _request(
        "POST",
        "/tasks",
        payload={"title": task_title, "description": "smoke", "project_id": project_id, "status": "to-do", "priority": "medium"},
    )
    task_id = created_task["id"]

    _, filtered_tasks = _request("GET", "/tasks", query={"project_id": project_id, "status": "to-do"})
    assert isinstance(filtered_tasks, list)
    assert any(task["id"] == task_id for task in filtered_tasks)

    _, updated_task = _request("PUT", f"/tasks/{task_id}", payload={"status": "in-progress"})
    assert updated_task["status"] == "in-progress"

    delete_task_status, _ = _request("DELETE", f"/tasks/{task_id}")
    assert delete_task_status == 204

    delete_project_status, _ = _request("DELETE", f"/projects/{project_id}")
    assert delete_project_status == 204

    print("API CRUD smoke check passed.")


if __name__ == "__main__":
    main()

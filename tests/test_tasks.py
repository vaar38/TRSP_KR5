import pytest
from fastapi.testclient import TestClient

HEADERS = {"X-User-Id": "10"}
HEADERS_2 = {"X-User-Id": "20"}


def create_task(client, title="Test task", priority=3, headers=None):
    headers = headers or HEADERS
    return client.post(
        "/tasks",
        json={"title": title, "status": "todo", "priority": priority},
        headers=headers,
    )


# 1. Успешное создание задачи
def test_create_task_success(client):
    resp = create_task(client, title="Подготовить тесты", priority=4)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Подготовить тесты"
    assert data["owner_id"] == 10
    assert data["id"] == 1


# 2. Ошибка 422 если title короче 3 символов
def test_create_task_short_title(client):
    resp = client.post(
        "/tasks",
        json={"title": "AB", "status": "todo", "priority": 3},
        headers=HEADERS,
    )
    assert resp.status_code == 422


# 3. Ошибка 401 если нет заголовка X-User-Id
def test_create_task_no_auth(client):
    resp = client.post(
        "/tasks",
        json={"title": "Valid title", "status": "todo", "priority": 3},
    )
    assert resp.status_code == 401


# 4. Пользователь видит только свои задачи
def test_user_sees_only_own_tasks(client):
    create_task(client, "User 10 task", headers=HEADERS)
    create_task(client, "User 20 task", headers=HEADERS_2)

    resp = client.get("/tasks", headers=HEADERS)
    tasks = resp.json()
    assert all(t["owner_id"] == 10 for t in tasks)
    assert len(tasks) == 1


# 5. Фильтрация задач по status и min_priority
def test_filter_by_status(client):
    create_task(client, "Task 1", priority=2, headers=HEADERS)
    r2 = create_task(client, "Task 2", priority=4, headers=HEADERS)
    task_id = r2.json()["id"]
    client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "done"},
        headers=HEADERS,
    )

    resp = client.get("/tasks?status=done", headers=HEADERS)
    assert all(t["status"] == "done" for t in resp.json())


def test_filter_by_min_priority(client):
    create_task(client, "Low priority", priority=1)
    create_task(client, "High priority", priority=5)

    resp = client.get("/tasks?min_priority=4", headers=HEADERS)
    tasks = resp.json()
    assert all(t["priority"] >= 4 for t in tasks)
    assert len(tasks) == 1


# 6. Успешное изменение статуса задачи
def test_update_task_status(client):
    task_id = create_task(client).json()["id"]
    resp = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "in_progress"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


# 7. Ошибка 404 при обращении к чужой или несуществующей задаче
def test_get_foreign_task_returns_404(client):
    task_id = create_task(client, headers=HEADERS_2).json()["id"]
    resp = client.get(f"/tasks/{task_id}", headers=HEADERS)
    assert resp.status_code == 404


def test_get_nonexistent_task_returns_404(client):
    resp = client.get("/tasks/9999", headers=HEADERS)
    assert resp.status_code == 404


# 8. Успешное удаление задачи
def test_delete_task(client):
    task_id = create_task(client).json()["id"]
    resp = client.delete(f"/tasks/{task_id}", headers=HEADERS)
    assert resp.status_code == 204

    # Confirm it's gone
    resp = client.get(f"/tasks/{task_id}", headers=HEADERS)
    assert resp.status_code == 404

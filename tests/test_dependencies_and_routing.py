import pytest

ADMIN_HEADERS = {"X-User-Id": "1", "X-User-Role": "admin"}
USER_HEADERS = {"X-User-Id": "10", "X-User-Role": "user"}
USER2_HEADERS = {"X-User-Id": "20", "X-User-Role": "user"}


def make_task(client, headers=None, title="Some task", priority=3):
    headers = headers or USER_HEADERS
    return client.post(
        "/tasks",
        json={"title": title, "status": "todo", "priority": priority},
        headers=headers,
    ).json()


# 1. /users/me возвращает текущего пользователя
def test_users_me(client):
    resp = client.get("/users/me", headers=USER_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 10
    assert data["role"] == "user"


# 2. Пользователь без заголовка X-User-Id получает 401
def test_users_me_no_auth(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401


# 3. Обычный пользователь получает 403 при обращении к /admin/stats
def test_admin_stats_forbidden_for_user(client):
    resp = client.get("/admin/stats", headers=USER_HEADERS)
    assert resp.status_code == 403


# 4. Администратор получает статистику по всем задачам
def test_admin_stats_for_admin(client):
    make_task(client, USER_HEADERS, "Task 1")
    make_task(client, USER2_HEADERS, "Task 2")

    resp = client.get("/admin/stats", headers=ADMIN_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_tasks"] == 2
    assert "todo" in data["by_status"]


# 5. Обычный пользователь не может удалить чужую задачу через /tasks/{task_id}
def test_user_cannot_delete_foreign_task(client):
    task = make_task(client, USER2_HEADERS, "User2 task")
    resp = client.delete(f"/tasks/{task['id']}", headers=USER_HEADERS)
    assert resp.status_code == 404


# 6. Администратор может удалить чужую задачу через /admin/tasks/{task_id}
def test_admin_can_delete_any_task(client):
    task = make_task(client, USER_HEADERS, "User task")
    resp = client.delete(f"/admin/tasks/{task['id']}", headers=ADMIN_HEADERS)
    assert resp.status_code == 204


# 7. /health маршрут
def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "env" in data

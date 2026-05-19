def test_users_me_returns_current_user(client):
    response = client.get("/users/me", headers={"X-User-Id": "42", "X-User-Role": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 42
    assert data["role"] == "admin"

def test_users_me_unauthorized_without_header(client):
    response = client.get("/users/me")
    assert response.status_code == 422

def test_admin_stats_forbidden_for_user(client):
    response = client.get("/admin/stats", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert response.status_code == 403

def test_admin_stats_success_for_admin(client):
    client.post("/tasks/", json={"title": "Task 1", "priority": 3, "status": "todo"}, headers={"X-User-Id": "10"})
    client.post("/tasks/", json={"title": "Task 2", "priority": 4, "status": "in_progress"}, headers={"X-User-Id": "20"})
    client.post("/tasks/", json={"title": "Task 3", "priority": 5, "status": "done"}, headers={"X-User-Id": "30"})
    
    response = client.get("/admin/stats", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 3
    assert data["by_status"]["todo"] == 1
    assert data["by_status"]["in_progress"] == 1
    assert data["by_status"]["done"] == 1

def test_user_cannot_delete_foreign_task(client):
    create_resp = client.post("/tasks/", json={"title": "Task", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert response.status_code == 404

def test_admin_can_delete_any_task(client):
    create_resp = client.post("/tasks/", json={"title": "Task", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    
    response = client.delete(f"/admin/tasks/{task_id}", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert response.status_code == 204
    
    get_resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert get_resp.status_code == 404
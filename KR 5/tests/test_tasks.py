def test_create_task_success(client):
    response = client.post(
        "/tasks/",
        json={"title": "New Task", "priority": 3, "status": "todo"},
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert data["priority"] == 3
    assert data["owner_id"] == 10
    assert "id" in data

def test_create_task_short_title(client):
    response = client.post(
        "/tasks/",
        json={"title": "No", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 422

def test_create_task_no_user_id(client):
    response = client.post(
        "/tasks/",
        json={"title": "New Task", "priority": 3}
    )
    assert response.status_code == 422

def test_user_sees_only_own_tasks(client):
    client.post("/tasks/", json={"title": "Task 10", "priority": 3}, headers={"X-User-Id": "10"})
    client.post("/tasks/", json={"title": "Task 20", "priority": 3}, headers={"X-User-Id": "20"})
    
    response = client.get("/tasks/", headers={"X-User-Id": "10"})
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task 10"

def test_filter_tasks_by_status_and_priority(client):
    client.post("/tasks/", json={"title": "High todo", "priority": 5, "status": "todo"}, headers={"X-User-Id": "10"})
    client.post("/tasks/", json={"title": "Low todo", "priority": 2, "status": "todo"}, headers={"X-User-Id": "10"})
    client.post("/tasks/", json={"title": "Done task", "priority": 4, "status": "done"}, headers={"X-User-Id": "10"})
    
    response = client.get("/tasks/?status=todo&min_priority=3", headers={"X-User-Id": "10"})
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "High todo"

def test_update_task_status(client):
    create_resp = client.post("/tasks/", json={"title": "To update", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    
    response = client.patch(f"/tasks/{task_id}/status", json={"status": "done"}, headers={"X-User-Id": "10"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"

def test_access_foreign_task_404(client):
    create_resp = client.post("/tasks/", json={"title": "Own task", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    
    response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert response.status_code == 404

def test_delete_task_success(client):
    create_resp = client.post("/tasks/", json={"title": "To delete", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]
    
    delete_resp = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert delete_resp.status_code == 204
    
    get_resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert get_resp.status_code == 404
import pytest
from app.main import fake_db, current_id

@pytest.fixture(autouse=True)
def clear_db():
    fake_db.clear()
    global current_id
    current_id = 1
    yield
    fake_db.clear()
    current_id = 1

def test_create_item(client):
    response = client.post("/items/", json={"name": "Айфончик 💅", "price": 99999.99})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Айфончик 💅"
    assert data["price"] == 99999.99
    assert "id" in data

def test_get_item(client):
    create_response = client.post("/items/", json={"name": "Нищий андройд 🤢", "price": 19999.99})
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Нищий андройд 🤢"

def test_get_item_not_found(client):
    response = client.get("/items/999")
    assert response.status_code == 404

def test_delete_item(client):
    create_response = client.post("/items/", json={"name": "Чехол для телефона", "price": 999.99})
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404

def test_delete_item_not_found(client):
    response = client.delete("/items/999")
    assert response.status_code == 404
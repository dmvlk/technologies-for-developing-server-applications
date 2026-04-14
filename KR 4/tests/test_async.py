import pytest
from faker import Faker
from app.main import fake_db, current_id

fake = Faker()

@pytest.fixture(autouse=True)
def clear_db():
    """Очищает БД ПЕРЕД каждым тестом"""
    fake_db.clear()
    global current_id
    current_id = 1
    yield
    fake_db.clear()
    current_id = 1

@pytest.mark.asyncio
async def test_async_create_item(async_client):
    payload = {"name": fake.name(), "price": fake.random_int(min=10, max=1000)}
    response = await async_client.post("/items/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["price"] == payload["price"]
    assert data["id"] == 1

@pytest.mark.asyncio
async def test_async_get_item(async_client):
    create_response = await async_client.post("/items/", json={"name": "Ноутбук", "price": 79999.99})
    assert create_response.status_code == 201
    
    item_id = create_response.json()["id"]
    response = await async_client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Ноутбук"
    assert response.json()["id"] == item_id

@pytest.mark.asyncio
async def test_async_delete_item(async_client):
    create_response = await async_client.post("/items/", json={"name": "Моноблок", "price": 79999.99})
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    delete_response = await async_client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 204
    
    get_response = await async_client.get(f"/items/{item_id}")
    assert get_response.status_code == 404
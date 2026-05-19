import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import storage

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(autouse=True)
def clear_storage():
    storage.clear()
    yield
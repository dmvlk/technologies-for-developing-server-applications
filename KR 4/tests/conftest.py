import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, 
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        yield ac
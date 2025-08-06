from fastapi.testclient import TestClient
from src.main import app  
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="module")
async def sync_client():
    return TestClient

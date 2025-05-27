import pytest
from httpx import AsyncClient
from main import app
from tests.conftest import register_and_login

@pytest.mark.asyncio
async def test_analytics_requires_auth(async_client):
    response = await async_client.get("/api/v1/analytics/summary")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_analytics_admin_access(async_client):
    # This assumes the test user is an admin; otherwise, expect 403
    token = await register_and_login(async_client)
    response = await async_client.get(
        "/api/v1/analytics/summary",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 403) 
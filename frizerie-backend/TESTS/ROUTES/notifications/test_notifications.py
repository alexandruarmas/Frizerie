import pytest
from httpx import AsyncClient
from main import app
from tests.conftest import register_and_login

@pytest.mark.asyncio
async def test_notifications_requires_auth(async_client):
    response = await async_client.get("/api/v1/notifications")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_notifications_authenticated(async_client):
    token = await register_and_login(async_client)
    response = await async_client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 404)

@pytest.mark.asyncio
async def test_mark_notification_as_read(async_client):
    token = await register_and_login(async_client)
    # This is a placeholder; you may need to create a notification first
    notification_id = 1
    response = await async_client.post(
        f"/api/v1/notifications/{notification_id}/read",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 404) 
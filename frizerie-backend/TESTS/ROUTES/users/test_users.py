import pytest
from httpx import AsyncClient
from main import app
from tests.conftest import register_and_login

@pytest.mark.asyncio
async def test_users_requires_auth(async_client):
    response = await async_client.get("/api/v1/users")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_user_profile_authenticated(async_client):
    token = await register_and_login(async_client)
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "email" in response.json()

@pytest.mark.asyncio
async def test_forbidden_access_to_other_user(async_client):
    token = await register_and_login(async_client)
    # Try to access another user's data (id=9999 should not exist or not belong to test user)
    response = await async_client.get(
        "/api/v1/users/9999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (403, 404) 
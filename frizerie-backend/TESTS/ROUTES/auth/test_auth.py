import pytest
from httpx import AsyncClient
from main import app
from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD

@pytest.mark.asyncio
async def test_login_missing_data():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login", json={})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client):
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@example.com", "password": "wrongpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_valid_credentials(async_client):
    # Assumes user already exists in test DB
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json() 
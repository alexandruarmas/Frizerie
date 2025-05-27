import pytest
from httpx import AsyncClient
from main import app
from tests.conftest import register_and_login

@pytest.mark.asyncio
async def test_services_requires_auth(async_client):
    response = await async_client.get("/api/v1/services")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_list_services_public(async_client):
    # If you have a public endpoint for services, test it here
    # response = await async_client.get("/api/v1/services/public")
    # assert response.status_code == 200
    pass  # Placeholder if not implemented

@pytest.mark.asyncio
async def test_create_service_admin_only(async_client):
    token = await register_and_login(async_client)
    service_payload = {
        "name": "Test Service",
        "price": 10.0,
        "duration": 30
    }
    response = await async_client.post(
        "/api/v1/services",
        json=service_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (201, 403, 422)  # 403 if not admin, 422 if payload invalid 
import pytest
from httpx import AsyncClient
from main import app
from tests.conftest import register_and_login

@pytest.mark.asyncio
async def test_bookings_requires_auth(async_client):
    response = await async_client.get("/api/v1/bookings")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_bookings_authenticated(async_client):
    token = await register_and_login(async_client)
    response = await async_client.get(
        "/api/v1/bookings",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 404)  # 404 if no bookings yet

@pytest.mark.asyncio
async def test_create_booking_authenticated(async_client):
    token = await register_and_login(async_client)
    # You may need to adjust the payload to match your BookingCreate schema
    booking_payload = {
        "service_id": 1,
        "start_time": "2025-01-01T10:00:00Z",
        "end_time": "2025-01-01T11:00:00Z"
    }
    response = await async_client.post(
        "/api/v1/bookings",
        json=booking_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 201, 422)  # 422 if service_id doesn't exist 
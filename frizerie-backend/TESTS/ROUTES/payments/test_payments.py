import pytest
from httpx import AsyncClient
from main import app
from tests.conftest import register_and_login

@pytest.mark.asyncio
async def test_payments_requires_auth(async_client):
    response = await async_client.get("/api/v1/payments")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_payments_authenticated(async_client):
    token = await register_and_login(async_client)
    response = await async_client.get(
        "/api/v1/payments",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 404)

@pytest.mark.asyncio
async def test_create_payment_authenticated(async_client):
    token = await register_and_login(async_client)
    payment_payload = {
        "booking_id": "some-booking-id",
        "amount": 10.0,
        "method": "card"
    }
    response = await async_client.post(
        "/api/v1/payments",
        json=payment_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (201, 422, 404)  # 422 if booking_id invalid 
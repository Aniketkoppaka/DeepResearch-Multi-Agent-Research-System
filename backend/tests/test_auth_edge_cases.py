import pytest
import asyncio
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_expired_and_invalid_tokens(client: AsyncClient):
    # 1. Invalid Access Token
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert resp.status_code == 401

    # 2. Invalid Refresh Token
    client.cookies.set("refresh_token", "invalid_refresh_token")
    resp = await client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401

    # 3. Missing Refresh Token
    client.cookies.clear()
    resp = await client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401

import pytest


@pytest.mark.asyncio
async def test_auth_flow_full(client):
    # 1. Register
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecureP!ss1",
            "full_name": "Test User"
        }
    )
    assert reg_resp.status_code == 201
    data = reg_resp.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

    # 2. Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecureP!ss1"
        }
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]

    # 3. Get /me (Protected)
    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "test@example.com"

    # 4. Unauthorized /me
    bad_me = await client.get("/api/v1/auth/me")
    assert bad_me.status_code == 401

@pytest.mark.asyncio
async def test_duplicate_registration(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "SecureP!ss1"}
    )
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "SecureP!ss1"}
    )
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_invalid_login(client):
    resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "WrongPass1"
        }
    )
    assert resp.status_code == 401

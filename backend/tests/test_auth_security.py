import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_refresh_token_rotation_and_revocation(client: AsyncClient):
    csrf_header = {"X-CSRF-Token": "testcsrf"}
    # 1. Register and Login
    reg = await client.post("/api/v1/auth/register", json={"email": "security@test.com", "password": "SecureSecret123!", "full_name": "Secure User"})
    assert reg.status_code == 201
    login = await client.post("/api/v1/auth/login", json={"email": "security@test.com", "password": "SecureSecret123!"})
    assert login.status_code == 200
    old_refresh_cookie = login.cookies.get("refresh_token")
    assert old_refresh_cookie is not None

    # 2. First Refresh (Rotation)
    client.cookies.set("refresh_token", old_refresh_cookie)
    refresh1 = await client.post("/api/v1/auth/refresh", headers=csrf_header)
    assert refresh1.status_code == 200
    new_refresh_cookie = refresh1.cookies.get("refresh_token")
    assert new_refresh_cookie != old_refresh_cookie

    # 3. Attempt Reuse of Old Refresh Token (MUST FAIL)
    client.cookies.set("refresh_token", old_refresh_cookie)
    reuse_resp = await client.post("/api/v1/auth/refresh", headers=csrf_header)
    assert reuse_resp.status_code == 401

    # 4. Logout Session Revocation
    client.cookies.set("refresh_token", new_refresh_cookie)
    logout = await client.post("/api/v1/auth/logout", headers=csrf_header)
    assert logout.status_code == 200


    # 5. Attempt Refresh After Logout (MUST FAIL)
    client.cookies.set("refresh_token", new_refresh_cookie)
    post_logout_refresh = await client.post("/api/v1/auth/refresh", headers=csrf_header)
    assert post_logout_refresh.status_code == 401

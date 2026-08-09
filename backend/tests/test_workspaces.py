import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_workspace_crud_and_security(client: AsyncClient):
    # 1. Register User A and User B
    reg_a = await client.post("/api/v1/auth/register", json={"email": "user_a@test.com", "password": "UserAPass123!", "full_name": "User A"})
    assert reg_a.status_code == 201
    login_a = await client.post("/api/v1/auth/login", json={"email": "user_a@test.com", "password": "UserAPass123!"})
    assert login_a.status_code == 200
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    reg_b = await client.post("/api/v1/auth/register", json={"email": "user_b@test.com", "password": "UserBPass123!", "full_name": "User B"})
    assert reg_b.status_code == 201
    login_b = await client.post("/api/v1/auth/login", json={"email": "user_b@test.com", "password": "UserBPass123!"})
    assert login_b.status_code == 200
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 2. Create Workspace as User A
    create_res = await client.post(
        "/api/v1/workspaces",
        headers=headers_a,
        json={"title": "User A Research", "description": "Private project", "research_mode": "Academic"},
    )
    assert create_res.status_code == 201
    ws_a = create_res.json()
    ws_a_id = ws_a["id"]
    assert ws_a["title"] == "User A Research"
    assert ws_a["research_mode"] == "Academic"

    # 3. List Workspaces for User A and User B
    list_a = await client.get("/api/v1/workspaces", headers=headers_a)
    assert list_a.status_code == 200
    assert len(list_a.json()) == 1

    list_b = await client.get("/api/v1/workspaces", headers=headers_b)
    assert list_b.status_code == 200
    assert len(list_b.json()) == 0

    # 4. IDOR Protection: User B attempts to access User A's workspace
    get_cross = await client.get(f"/api/v1/workspaces/{ws_a_id}", headers=headers_b)
    assert get_cross.status_code == 404
    assert get_cross.json()["detail"] == "Workspace not found"

    patch_cross = await client.patch(f"/api/v1/workspaces/{ws_a_id}", headers=headers_b, json={"title": "Hacked"})
    assert patch_cross.status_code == 404

    del_cross = await client.delete(f"/api/v1/workspaces/{ws_a_id}", headers=headers_b)
    assert del_cross.status_code == 404

    # 5. User A updates own workspace
    update_a = await client.patch(f"/api/v1/workspaces/{ws_a_id}", headers=headers_a, json={"title": "Updated User A Research"})
    assert update_a.status_code == 200
    assert update_a.json()["title"] == "Updated User A Research"

    # 6. Delete Workspace
    del_a = await client.delete(f"/api/v1/workspaces/{ws_a_id}", headers=headers_a)
    assert del_a.status_code == 204

    # Verify deleted
    get_deleted = await client.get(f"/api/v1/workspaces/{ws_a_id}", headers=headers_a)
    assert get_deleted.status_code == 404

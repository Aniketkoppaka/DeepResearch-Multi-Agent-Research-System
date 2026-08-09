import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_document_upload_validation_and_security(client: AsyncClient):
    # 1. Setup User A and User B with workspaces
    login_a_res = await client.post("/api/v1/auth/register", json={"email": "doc_user_a@test.com", "password": "DocUserAPass123!", "full_name": "Doc User A"})
    assert login_a_res.status_code == 201
    auth_a = await client.post("/api/v1/auth/login", json={"email": "doc_user_a@test.com", "password": "DocUserAPass123!"})
    token_a = auth_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    login_b_res = await client.post("/api/v1/auth/register", json={"email": "doc_user_b@test.com", "password": "DocUserBPass123!", "full_name": "Doc User B"})
    assert login_b_res.status_code == 201
    auth_b = await client.post("/api/v1/auth/login", json={"email": "doc_user_b@test.com", "password": "DocUserBPass123!"})
    token_b = auth_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    ws_a = (await client.post("/api/v1/workspaces", headers=headers_a, json={"title": "Doc Workspace A"})).json()
    ws_a_id = ws_a["id"]

    # 2. Upload valid PDF document
    pdf_content = b"%PDF-1.4 header text and valid document bytes"
    files = {"file": ("test_paper.pdf", pdf_content, "application/pdf")}
    upload_res = await client.post(f"/api/v1/workspaces/{ws_a_id}/documents", headers=headers_a, files=files)
    assert upload_res.status_code == 201
    doc_data = upload_res.json()
    assert doc_data["filename"] == "test_paper.pdf"
    assert doc_data["mime_type"] == "application/pdf"
    doc_id = doc_data["id"]

    # 3. List Documents
    list_docs = await client.get(f"/api/v1/workspaces/{ws_a_id}/documents", headers=headers_a)
    assert list_docs.status_code == 200
    assert len(list_docs.json()) == 1

    # 4. Error Case: Unsupported MIME type
    bad_type_files = {"file": ("script.py", b"print('hello')", "application/x-python")}
    bad_type_res = await client.post(f"/api/v1/workspaces/{ws_a_id}/documents", headers=headers_a, files=bad_type_files)
    assert bad_type_res.status_code == 400
    assert "Unsupported file type" in bad_type_res.json()["detail"]

    # 5. Error Case: Spoofed/Invalid Magic Bytes
    spoofed_files = {"file": ("malicious.pdf", b"NOT_A_PDF_HEADER_CONTENT", "application/pdf")}
    spoofed_res = await client.post(f"/api/v1/workspaces/{ws_a_id}/documents", headers=headers_a, files=spoofed_files)
    assert spoofed_res.status_code == 400
    assert "does not match" in spoofed_res.json()["detail"]

    # 6. IDOR Protection: User B attempts upload, list, and delete on User A's workspace
    cross_upload = await client.post(f"/api/v1/workspaces/{ws_a_id}/documents", headers=headers_b, files=files)
    assert cross_upload.status_code == 404

    cross_list = await client.get(f"/api/v1/workspaces/{ws_a_id}/documents", headers=headers_b)
    assert cross_list.status_code == 404

    cross_del = await client.delete(f"/api/v1/workspaces/{ws_a_id}/documents/{doc_id}", headers=headers_b)
    assert cross_del.status_code == 404

    # 7. User A deletes document
    del_doc = await client.delete(f"/api/v1/workspaces/{ws_a_id}/documents/{doc_id}", headers=headers_a)
    assert del_doc.status_code == 204

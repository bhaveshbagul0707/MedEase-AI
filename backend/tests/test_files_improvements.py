import os
import io
import types
import pytest

from app.services import storage_service as storage_module


@pytest.mark.asyncio
async def test_upload_size_enforcement(client, register_payload, monkeypatch):
    # Create a small max size via monkeypatch
    class MockSettings:
        uploads_dir = "./tmp_uploads"
        max_upload_size_bytes = 10
        allowed_mime_types = ["application/pdf"]

    monkeypatch.setattr(storage_module, "get_settings", lambda: MockSettings())

    # Register user and get token
    r = await client.post("/api/v1/auth/register", json=register_payload)
    assert r.status_code == 200
    token = r.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload file larger than 10 bytes
    big_content = b"X" * 1024
    files = {"file": ("big.pdf", io.BytesIO(big_content), "application/pdf")}
    resp = await client.post("/api/v1/files/upload", headers=headers, files=files)
    assert resp.status_code == 413


@pytest.mark.asyncio
async def test_no_absolute_path_and_download_and_duplicate(client, register_payload):
    # Register user and get token
    r = await client.post("/api/v1/auth/register", json=register_payload)
    assert r.status_code == 200
    token = r.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    content = b"dummy pdf content"
    files = {"file": ("doc.pdf", io.BytesIO(content), "application/pdf")}
    resp = await client.post("/api/v1/files/upload", headers=headers, files=files)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "download_url" in data and data["download_url"].startswith("/api/v1/files/")
    # Ensure storage_path not exposed
    assert "storage_path" not in data

    file_id = data["id"]
    # Download endpoint
    dl = await client.get(f"/api/v1/files/{file_id}/download", headers=headers)
    assert dl.status_code == 200
    assert dl.content == content

    # Upload duplicate
    resp2 = await client.post("/api/v1/files/upload", headers=headers, files=files)
    assert resp2.status_code == 200
    assert resp2.json()["message"] == "File already exists"
    assert resp2.json()["data"]["id"] == file_id

    # Ensure only one file in list
    lst = await client.get("/api/v1/files/", headers=headers)
    assert lst.status_code == 200
    assert lst.json()["data"]["total"] == 1


@pytest.mark.asyncio
async def test_delete_marks_deleted_and_enqueue_cleanup(client, register_payload):
    # Register user and get token
    r = await client.post("/api/v1/auth/register", json=register_payload)
    assert r.status_code == 200
    token = r.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    content = b"to delete"
    files = {"file": ("todelete.pdf", io.BytesIO(content), "application/pdf")}
    resp = await client.post("/api/v1/files/upload", headers=headers, files=files)
    assert resp.status_code == 200
    file_id = resp.json()["data"]["id"]

    # Delete
    d = await client.delete(f"/api/v1/files/{file_id}", headers=headers)
    assert d.status_code == 200
    assert d.json()["message"] == "File deletion initiated"

    # Fetch file and ensure status is DELETED
    g = await client.get(f"/api/v1/files/{file_id}", headers=headers)
    assert g.status_code == 200
    assert g.json()["data"]["status"] == "DELETED"

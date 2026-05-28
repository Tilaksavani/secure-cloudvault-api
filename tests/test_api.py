import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Secure CloudVault API is running"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_search_download_count_and_delete_file(client):
    file_content = b"sample cloud file content"

    upload_response = client.post(
        "/files",
        files={"file": ("resume-notes.txt", file_content, "text/plain")},
    )

    assert upload_response.status_code == 201
    uploaded = upload_response.json()

    assert uploaded["original_filename"] == "resume-notes.txt"
    assert uploaded["content_type"] == "text/plain"
    assert uploaded["size_bytes"] == len(file_content)
    assert uploaded["download_count"] == 0

    file_id = uploaded["id"]

    search_response = client.get("/files?search=resume")
    assert search_response.status_code == 200
    assert any(item["id"] == file_id for item in search_response.json())

    filter_response = client.get("/files?file_type=text")
    assert filter_response.status_code == 200
    assert any(item["id"] == file_id for item in filter_response.json())

    download_response = client.get(f"/files/{file_id}/download")
    assert download_response.status_code == 200
    assert download_response.content == file_content

    metadata_response = client.get(f"/files/{file_id}")
    assert metadata_response.status_code == 200
    assert metadata_response.json()["download_count"] == 1

    delete_response = client.delete(f"/files/{file_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "File deleted successfully"

    missing_response = client.get(f"/files/{file_id}")
    assert missing_response.status_code == 404


def test_empty_file_rejected(client):
    response = client.post(
        "/files",
        files={"file": ("empty.txt", b"", "text/plain")},
    )

    assert response.status_code == 400


def test_large_file_rejected(client):
    large_content = b"a" * (11 * 1024 * 1024)

    response = client.post(
        "/files",
        files={"file": ("large.txt", large_content, "text/plain")},
    )

    assert response.status_code == 413
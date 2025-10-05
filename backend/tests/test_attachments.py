import pytest
from fastapi import status
import io

ATTACHMENTS_URL = "/api/attachments"


@pytest.fixture
def test_task(client, normal_user_token_headers):
    """Create a test task for attachment testing."""
    # First create a project
    project = client.post(
        "/api/projects/",
        headers=normal_user_token_headers,
        json={
            "title": "Test Project",
            "description": "For attachment testing",
        },
    ).json()

    # Then create a task
    task = client.post(
        f"/api/projects/{project['id']}/tasks/",
        headers=normal_user_token_headers,
        json={
            "title": "Test Task",
            "description": "For attachments",
            "status": "todo",
        },
    ).json()
    return task


@pytest.fixture
def uploaded_attachment(client, normal_user_token_headers, test_task):
    """Create a test attachment for reuse in tests."""
    file_content = b"Test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post(
        f"{ATTACHMENTS_URL}/{test_task['id']}",
        headers=normal_user_token_headers,
        files=files,
    )
    return response.json()


def test_01_upload_attachment(client, normal_user_token_headers, test_task):
    """Test uploading a file attachment to a task."""
    file_content = b"Test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

    response = client.post(
        f"{ATTACHMENTS_URL}/{test_task['id']}",
        headers=normal_user_token_headers,
        files=files,
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["content_type"] == "text/plain"
    assert data["file_size"] == len(file_content)
    assert data["task_id"] == test_task["id"]
    assert "uploader_id" in data
    assert "created_at" in data


def test_02_get_task_attachments(
    client, normal_user_token_headers, test_task, uploaded_attachment
):
    """Test getting all attachments for a task."""
    response = client.get(
        f"{ATTACHMENTS_URL}/{test_task['id']}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["task_id"] == test_task["id"]


def test_03_download_attachment(
    client, normal_user_token_headers, test_task, uploaded_attachment
):
    """Test downloading an attachment."""
    response = client.get(
        f"{ATTACHMENTS_URL}/{test_task['id']}/{uploaded_attachment['id']}/download",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert b"Test file content" in response.content
    assert "Content-Disposition" in response.headers
    assert uploaded_attachment["filename"] in response.headers["Content-Disposition"]


def test_04_delete_attachment(
    client, normal_user_token_headers, test_task, uploaded_attachment
):
    """Test deleting an attachment."""
    response = client.delete(
        f"{ATTACHMENTS_URL}/{test_task['id']}/{uploaded_attachment['id']}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's gone
    response = client.get(
        f"{ATTACHMENTS_URL}/{test_task['id']}/{uploaded_attachment['id']}/download",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_05_upload_different_file_sizes(client, normal_user_token_headers, test_task):
    """Test uploading files of different sizes."""
    sizes = [1024, 1024 * 1024, 5 * 1024 * 1024]  # 1KB, 1MB, 5MB

    for size in sizes:
        content = b"x" * size
        files = {"file": (f"test_{size}.txt", io.BytesIO(content), "text/plain")}

        response = client.post(
            f"{ATTACHMENTS_URL}/{test_task['id']}",
            headers=normal_user_token_headers,
            files=files,
        )

        # Files up to 5MB should be accepted
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["file_size"] == size


def test_06_upload_invalid_file_type(client, normal_user_token_headers, test_task):
    """Test uploading a file with unsupported type."""
    file_content = b"Invalid file content"
    files = {"file": ("test.exe", io.BytesIO(file_content), "application/x-msdownload")}

    response = client.post(
        f"{ATTACHMENTS_URL}/{test_task['id']}",
        headers=normal_user_token_headers,
        files=files,
    )
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_07_bulk_delete_attachments(client, normal_user_token_headers, test_task):
    """Test deleting multiple attachments at once."""
    # Upload multiple attachments
    attachments = []
    for i in range(3):
        files = {"file": (f"test_{i}.txt", io.BytesIO(b"content"), "text/plain")}
        response = client.post(
            f"{ATTACHMENTS_URL}/{test_task['id']}",
            headers=normal_user_token_headers,
            files=files,
        )
        attachments.append(response.json())

    # Delete them in bulk
    attachment_ids = [a["id"] for a in attachments]
    response = client.post(
        f"{ATTACHMENTS_URL}/{test_task['id']}/bulk-delete",
        headers=normal_user_token_headers,
        json=attachment_ids,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "Successfully deleted" in data["message"]
    assert str(len(attachments)) in data["message"]

    # Verify they're all gone
    response = client.get(
        f"{ATTACHMENTS_URL}/{test_task['id']}",
        headers=normal_user_token_headers,
    )
    remaining = response.json()
    assert not any(a["id"] in attachment_ids for a in remaining)


def test_08_pagination(client, normal_user_token_headers, test_task):
    """Test attachment list pagination."""
    # Upload multiple attachments
    for i in range(5):
        files = {"file": (f"test_{i}.txt", io.BytesIO(b"content"), "text/plain")}
        client.post(
            f"{ATTACHMENTS_URL}/{test_task['id']}",
            headers=normal_user_token_headers,
            files=files,
        )

    # Test with different pagination parameters
    response = client.get(
        f"{ATTACHMENTS_URL}/{test_task['id']}?skip=2&limit=2",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) <= 2  # Should only return 2 items


def test_09_error_cases(client, normal_user_token_headers, test_task):
    """Test various error cases."""
    # Test non-existent task
    files = {"file": ("test.txt", io.BytesIO(b"content"), "text/plain")}
    response = client.post(
        f"{ATTACHMENTS_URL}/99999",
        headers=normal_user_token_headers,
        files=files,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Test too large file
    content = b"x" * (5 * 1024 * 1024 + 1)  # 5MB + 1 byte
    files = {"file": ("large.txt", io.BytesIO(content), "text/plain")}
    response = client.post(
        f"{ATTACHMENTS_URL}/{test_task['id']}",
        headers=normal_user_token_headers,
        files=files,
    )
    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    # Test non-existent attachment download
    response = client.get(
        f"{ATTACHMENTS_URL}/{test_task['id']}/99999/download",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

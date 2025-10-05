from fastapi import status
import json
import pytest

NOTIFICATIONS_URL = "/api/notifications/"
PROJECTS_URL = "/api/projects/"


@pytest.fixture(scope="function")
def task(client, superuser):
    """
    Create a project and a task for use in tests.
    Returns essential info about the created task and project.
    """

    user_headers = {"Authorization": f"Bearer {superuser['token']}"}

    project_resp = client.post(
        PROJECTS_URL,
        json={
            "title": "Test Project for Task",
            "description": "Temp",
            "owner_id": superuser["id"],
            "collaborator_ids": [],
        },
        headers=user_headers,
    )
    assert project_resp.status_code == 201
    project_id = project_resp.json()["id"]

    task_data = {
        "title": "Task for Attachment Test",
        "assigned_user_ids": [superuser["id"]],
        "priority": "low",
    }

    task_resp = client.post(
        f"{PROJECTS_URL}{project_id}/tasks/",
        json=task_data,
        headers=user_headers,
    )
    assert task_resp.status_code == 201
    task_data = task_resp.json()

    return {
        "task_id": task_data["id"],
        "project_id": project_id,
        "task_data": task_data,
        "headers": user_headers,
    }


@pytest.fixture
def sample_notifications(client, normal_user_token_headers, task):
    """Create sample notifications for testing."""
    notifications = []
    task_id = task["task_id"]
    project_id = task["project_id"]

    for i in range(3):
        response = client.post(
            NOTIFICATIONS_URL,
            headers=normal_user_token_headers,
            json={
                "type": "task_assigned",
                "title": f"Test Notification {i}",
                "message": f"Test message {i}",
                "related_task_id": task_id,
                "related_project_id": project_id,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        notifications.append(response.json())
    return notifications


def test_01_create_notification(client, normal_user_token_headers, task):
    """Test creating a notification."""
    task_id = task["task_id"]
    project_id = task["project_id"]
    response = client.post(
        NOTIFICATIONS_URL,
        headers=normal_user_token_headers,
        json={
            "type": "task_assigned",
            "title": "New Task Assignment",
            "message": "You have been assigned to a new task",
            "related_task_id": task_id,
            "related_project_id": project_id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "New Task Assignment"
    assert data["read"] is False
    assert "created_at" in data
    assert "id" in data


def test_02_get_notifications_pagination(
    client, normal_user_token_headers, sample_notifications
):
    """Test notification pagination."""
    # Test default pagination
    response = client.get(NOTIFICATIONS_URL, headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) <= 100  # Default limit

    # Test custom pagination
    response = client.get(
        f"{NOTIFICATIONS_URL}?skip=1&limit=2", headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) <= 2


def test_03_mark_notification_as_read(client, normal_user_token_headers, task):
    """Test marking a notification as read."""
    # Create notification
    task_id = task["task_id"]
    project_id = task["project_id"]
    notification = client.post(
        NOTIFICATIONS_URL,
        headers=normal_user_token_headers,
        json={
            "type": "task_assigned",
            "title": "Test Notification",
            "message": "Test message",
            "related_task_id": task_id,
            "related_project_id": project_id,
        },
    ).json()

    # Mark as read
    response = client.post(
        f"{NOTIFICATIONS_URL}{notification['id']}/read",
        headers=normal_user_token_headers,
        json={},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["read"] is True
    assert data["read_at"] is not None


def test_04_mark_all_notifications_read(
    client, normal_user_token_headers, sample_notifications
):
    """Test marking all notifications as read."""
    # Mark all as read
    response = client.post(
        f"{NOTIFICATIONS_URL}mark-all-read", headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify all are read
    notifications = client.get(
        NOTIFICATIONS_URL, headers=normal_user_token_headers
    ).json()
    assert all(n["read"] for n in notifications)


def test_05_get_notifications_by_type(client, normal_user_token_headers, task):
    """Test filtering notifications by type."""
    # Create notifications of different types
    task_id = task["task_id"]
    project_id = task["project_id"]
    types = ["task_assigned", "task_comment", "task_status_changed"]
    for notification_type in types:
        client.post(
            NOTIFICATIONS_URL,
            headers=normal_user_token_headers,
            json={
                "type": notification_type,
                "title": f"Test {notification_type}",
                "message": f"Test message for {notification_type}",
                "related_task_id": task_id,
                "related_project_id": project_id,
            },
        )

    # Test filtering by each type
    for notification_type in types:
        response = client.get(
            f"{NOTIFICATIONS_URL}?notification_type={notification_type}",
            headers=normal_user_token_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(n["type"] == notification_type for n in data)


def test_06_delete_notification(client, normal_user_token_headers, task):
    """Test deleting a notification."""
    # Create notification
    task_id = task["task_id"]
    project_id = task["project_id"]
    notification = client.post(
        NOTIFICATIONS_URL,
        headers=normal_user_token_headers,
        json={
            "type": "task_assigned",
            "title": "To Delete",
            "message": "This will be deleted",
            "related_task_id": task_id,
            "related_project_id": project_id,
        },
    ).json()

    # Delete it
    response = client.delete(
        f"{NOTIFICATIONS_URL}{notification['id']}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's gone
    response = client.get(NOTIFICATIONS_URL, headers=normal_user_token_headers)
    data = response.json()
    assert not any(n["id"] == notification["id"] for n in data)


def test_07_bulk_delete_notifications(
    client, normal_user_token_headers, sample_notifications, task
):
    """Test deleting multiple notifications at once."""
    notification_ids = [n["id"] for n in sample_notifications[:2]]

    response = client.post(
        f"{NOTIFICATIONS_URL}bulk-delete",
        headers=normal_user_token_headers,
        json=notification_ids,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert (
        data["message"] == f"Successfully deleted {len(notification_ids)} notifications"
    )


def test_08_get_notifications_count(
    client, normal_user_token_headers, sample_notifications
):
    """Test getting notification counts."""
    response = client.get(
        f"{NOTIFICATIONS_URL}count", headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert data["total"] >= len(sample_notifications)

    # Test unread count
    response = client.get(
        f"{NOTIFICATIONS_URL}count?unread_only=true", headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data


def test_09_notification_error_cases(client, normal_user_token_headers):
    """Test error cases for notifications."""
    # Test invalid notification ID
    response = client.post(
        f"{NOTIFICATIONS_URL}999999/read",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Test invalid pagination parameters
    response = client.get(
        f"{NOTIFICATIONS_URL}?skip=-1", headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    response = client.get(
        f"{NOTIFICATIONS_URL}?limit=0", headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

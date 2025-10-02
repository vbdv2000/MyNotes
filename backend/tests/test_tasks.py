import pytest
from fastapi import status
from typing import Dict, Any

# --- Constants / URLs ---
TASK_URL = "/api/tasks/"
PROJECT_URL = "/api/projects/"
USER_URL = "/api/users/"

TASK_DATA: Dict[str, Any] = {
    "title": "Initial Task",
    "description": "This is the first task for testing.",
    "status": "todo"
}

USER_DATA = {
    "email": "taskowner@example.com",
    "password": "taskpassword",
    "full_name": "Task Owner",
    "is_superuser": False
}

PROJECT_DATA = {
    "title": "Test Project",
    "description": "Project for task tests"
}

# --- Fixtures ---

@pytest.fixture
def created_user_id(client):
    """Create a user and return the ID."""
    response = client.post(USER_URL, json=USER_DATA)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["id"]

@pytest.fixture
def created_project_id(client, created_user_id):
    """Create a project with owner and return the ID."""
    data = PROJECT_DATA.copy()
    data["owner_id"] = created_user_id
    data["collaborator_ids"] = []
    response = client.post(PROJECT_URL, json=data)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["id"]

@pytest.fixture
def created_task_id(client, created_project_id, created_user_id):
    """Create a task assigned to the user and return the task ID."""
    data = TASK_DATA.copy()
    data["project_id"] = created_project_id
    data["assigned_user_ids"] = [created_user_id]
    response = client.post(TASK_URL, json=data)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["id"]

# ==============================
#           CRUD Tests
# ==============================

def test_01_create_task(client, created_user_id, created_project_id):
    """Create a task and check its fields."""
    data = TASK_DATA.copy()
    data["project_id"] = created_project_id
    data["assigned_user_ids"] = [created_user_id]
    response = client.post(TASK_URL, json=data)
    assert response.status_code == status.HTTP_201_CREATED
    resp_data = response.json()
    assert resp_data["title"] == TASK_DATA["title"]
    assert resp_data["project_id"] == created_project_id
    assert resp_data["assigned_users"][0]["id"] == created_user_id

def test_02_create_task_invalid_user(client, created_project_id):
    """Fails when assigned_user_ids contains a non-existent user."""
    data = TASK_DATA.copy()
    data["project_id"] = created_project_id
    data["assigned_user_ids"] = [99999]  # Non-existent user
    response = client.post(TASK_URL, json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_03_read_task_by_id(client, created_task_id):
    """Retrieve a task by its ID."""
    response = client.get(f"{TASK_URL}{created_task_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created_task_id
    assert "title" in data

def test_04_read_tasks_list(client, created_task_id):
    """Retrieve the list of tasks and check if our task is present."""
    response = client.get(TASK_URL)
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()
    assert any(t["id"] == created_task_id for t in tasks)

def test_05_update_task(client, created_task_id, created_user_id):
    """Update a task's description, status, and assigned users."""
    update_data = {
        "description": "Updated description",
        "status": "done",
        "assigned_user_ids": [created_user_id]
    }
    response = client.patch(f"{TASK_URL}{created_task_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["status"] == "done"
    assert data["assigned_users"][0]["id"] == created_user_id

def test_06_delete_task(client, created_task_id):
    """Delete a task and verify it no longer exists."""
    response = client.delete(f"{TASK_URL}{created_task_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Verify deletion
    check = client.get(f"{TASK_URL}{created_task_id}")
    assert check.status_code == status.HTTP_404_NOT_FOUND

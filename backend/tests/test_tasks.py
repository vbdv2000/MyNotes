import pytest
from fastapi import status
from typing import Dict, Any

# The 'client' and 'db' fixtures are automatically found from conftest.py

# --- Constants and Test Data ---

TASK_URL = "/api/tasks/"
TASK_DATA: Dict[str, Any] = {
    "title": "Initial Task",
    "description": "This is the first task for testing.",
    "status": "todo", # Assuming a simple status field (todo, in-progress, done)
    # owner_id must be added dynamically
}
USER_DATA = {
    "email": "taskowner@example.com",
    "password": "taskpassword",
    "full_name": "Task Owner",
    "is_superuser": False
}
USER_URL = "/api/users/"

# --- Fixture to Create User and Get ID ---
@pytest.fixture
def created_user_id(client):
    """
    Creates a user to be the task owner and returns their ID.
    """
    response = client.post(USER_URL, json=USER_DATA)
    # If user creation fails here, something is wrong with the user CRUD
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["id"]

# --- Fixture to Create Task and Get ID ---
@pytest.fixture
def created_task_id(client, created_user_id):
    """
    Creates a task associated with the user and returns its ID.
    """
    data = TASK_DATA.copy()
    data["owner_id"] = created_user_id # Assign the owner's ID
    
    response = client.post(TASK_URL, json=data)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["id"]


# ==============================
#           CRUD Tests
# ==============================

def test_create_task(client, created_user_id):
    """Test POST /api/tasks/ to create a task."""
    data = TASK_DATA.copy()
    data["owner_id"] = created_user_id
    
    response = client.post(TASK_URL, json=data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["title"] == TASK_DATA["title"]
    assert data["owner_id"] == created_user_id


def test_create_task_invalid_user(client):
    """Test POST /api/tasks/ with a non-existent owner_id (should fail with 404)."""
    data = TASK_DATA.copy()
    data["owner_id"] = 99999 # Non-existent ID
    
    response = client.post(TASK_URL, json=data)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]


def test_read_task_by_id(client, created_task_id):
    """Test GET /api/tasks/{task_id}."""
    
    response = client.get(f"{TASK_URL}{created_task_id}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == created_task_id
    assert response.json()["title"] == TASK_DATA["title"]


def test_read_tasks_list(client, created_task_id, created_user_id):
    """Test GET /api/tasks/ to list all tasks."""
    # created_task_id fixture ensures at least one task exists.
    
    response = client.get(TASK_URL)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 1
    assert response.json()[0]["owner_id"] == created_user_id


def test_update_task(client, created_task_id):
    """Test PATCH /api/tasks/{task_id} to update task status and description."""
    
    update_data = {
        "description": "Updated description and status.",
        "status": "done"
    }
    response = client.patch(f"{TASK_URL}{created_task_id}", json=update_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created_task_id
    assert data["description"] == update_data["description"]
    assert data["status"] == update_data["status"]


def test_delete_task(client, created_task_id):
    """Test DELETE /api/tasks/{task_id}."""
    
    # 1. Delete the task
    response = client.delete(f"{TASK_URL}{created_task_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # 2. Verify the task no longer exists
    check_response = client.get(f"{TASK_URL}{created_task_id}")
    assert check_response.status_code == status.HTTP_404_NOT_FOUND
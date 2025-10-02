import pytest
from fastapi import status
from typing import Dict, Any, List

# --- Constantes y URLs ---

PROJECT_URL = "/api/projects/"
USER_URL = "/api/users/"
TASK_URL = "/api/tasks/"

# Datos base para la creación
BASE_USER_DATA = {
    "password": "securepassword",
    "full_name": "Test User",
    "is_superuser": False
}
PROJECT_DATA: Dict[str, Any] = {
    "title": "Validated Project System",
    "description": "Project to test team assignments."
}

# --- Fixtures de Usuarios (Necesarias para todas las pruebas) ---

def create_user(client, email: str, full_name: str) -> int:
    """Función helper para crear un usuario y devolver su ID."""
    data = BASE_USER_DATA.copy()
    data["email"] = email
    data["full_name"] = full_name
    response = client.post(USER_URL, json=data)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["id"]

@pytest.fixture(scope="function")
def created_owner_id(client):
    """ID of the user who will be the Project Owner."""
    return create_user(client, "project.owner@test.com", "Project Owner")

@pytest.fixture(scope="function")
def created_collaborator_id(client):
    """ID of the user who will be a Collaborator in the project."""
    return create_user(client, "project.collab@test.com", "Project Collaborator")

@pytest.fixture(scope="function")
def created_unrelated_user_id(client):
    """ID of a user who is NOT a member of the project team."""
    return create_user(client, "unrelated.user@test.com", "Unrelated User")

# --- Fixture de Project ---

@pytest.fixture(scope="function")
def created_project_data(client, created_owner_id, created_collaborator_id):
    """
    Creates a project with an owner and a collaborator. Returns the response data.
    This project will be used in task assignment tests.
    """
    data = PROJECT_DATA.copy()
    data["owner_id"] = created_owner_id
    data["collaborator_ids"] = [created_collaborator_id]
    
    response = client.post(PROJECT_URL, json=data)
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()

@pytest.fixture(scope="function")
def created_project_id(created_project_data):
    """Returns the ID of the created project."""
    return created_project_data["id"]

# ==================================================
# Tests CRUD
# ==================================================

def test_01_create_project_success(created_project_data, created_owner_id, created_collaborator_id):
    """Test POST /api/projects/ to create a project successfully."""
    data = created_project_data
    
    assert data["title"] == PROJECT_DATA["title"]
    assert data["owner_id"] == created_owner_id
    
    collaborator_ids = [c["id"] for c in data["collaborators"]]
    assert len(collaborator_ids) == 1
    assert created_collaborator_id in collaborator_ids
    assert data["owner"]["id"] == created_owner_id

def test_02_create_project_invalid_owner_fails(client):
    """Creation should fail if the owner_id does not exist (404)."""
    data = PROJECT_DATA.copy()
    data["owner_id"] = 99999
    
    response = client.post(PROJECT_URL, json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Owner ID 99999 not found" in response.json()["detail"]

def test_03_create_project_owner_is_collaborator_fails(client, created_owner_id):
    """Creation should fail if the owner is listed as a collaborator (400)."""
    data = PROJECT_DATA.copy()
    data["owner_id"] = created_owner_id
    data["collaborator_ids"] = [created_owner_id] 
    
    response = client.post(PROJECT_URL, json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Owner cannot be listed as a collaborator" in response.json()["detail"]

def test_04_update_project_collaborators(client, created_project_id, created_owner_id, created_collaborator_id):
    """Test updating the list of collaborators (full replacement)."""

    # 1. Create a new user to be the new collaborator
    new_collab_id = create_user(client, "new.collab@test.com", "New Collaborator")

    # 2. Replace existing collaborator with the new one
    update_data = {"collaborator_ids": [new_collab_id]}
    response = client.patch(f"{PROJECT_URL}{created_project_id}", json=update_data)
    
    assert response.status_code == status.HTTP_200_OK
    collab_ids = [c["id"] for c in response.json()["collaborators"]]
    assert len(collab_ids) == 1
    assert new_collab_id in collab_ids # The new one is there
    assert created_collaborator_id not in collab_ids # The old one was removed

    # 3. Clear all collaborators
    update_data = {"collaborator_ids": []}
    response = client.patch(f"{PROJECT_URL}{created_project_id}", json=update_data)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["collaborators"] == []
    
    update_data = {"collaborator_ids": [created_owner_id]}
    response = client.patch(f"{PROJECT_URL}{created_project_id}", json=update_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

# ==================================================
# TASK BASED TESTS
# ==================================================

TASK_BASE_CREATE = {
    "title": "New Task for Project",
    "status": "todo",
    "description": "Test assignment validation"
}

def test_05_create_task_assigned_to_owner_success(client, created_project_id, created_owner_id):
    """Test POST /api/tasks/ to create a task assigned to the project owner."""
    task_data = TASK_BASE_CREATE.copy()
    task_data["project_id"] = created_project_id
    task_data["assigned_user_ids"] = [created_owner_id]
    
    response = client.post(TASK_URL, json=task_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assigned_ids = [u["id"] for u in data["assigned_users"]]
    assert created_owner_id in assigned_ids

def test_06_create_task_assigned_to_collaborator_success(client, created_project_id, created_collaborator_id):
    """Test POST /api/tasks/ to create a task assigned to a collaborator."""
    task_data = TASK_BASE_CREATE.copy()
    task_data["project_id"] = created_project_id
    task_data["assigned_user_ids"] = [created_collaborator_id]
    
    response = client.post(TASK_URL, json=task_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    assigned_ids = [u["id"] for u in response.json()["assigned_users"]]
    assert created_collaborator_id in assigned_ids

def test_07_create_task_assigned_to_multiple_team_members_success(client, created_project_id, created_owner_id, created_collaborator_id):
    """Test POST /api/tasks/ to create a task assigned to multiple valid members (Owner + Collab)."""
    task_data = TASK_BASE_CREATE.copy()
    task_data["project_id"] = created_project_id
    task_data["assigned_user_ids"] = [created_owner_id, created_collaborator_id]
    
    response = client.post(TASK_URL, json=task_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    assigned_ids = {u["id"] for u in response.json()["assigned_users"]}
    assert assigned_ids == {created_owner_id, created_collaborator_id}

def test_08_create_task_assigned_to_unrelated_user_fails(client, created_project_id, created_unrelated_user_id):
    """Test POST /api/tasks/ to create a task assigned to a user who is NOT part of the team (400)."""
    task_data = TASK_BASE_CREATE.copy()
    task_data["project_id"] = created_project_id
    task_data["assigned_user_ids"] = [created_unrelated_user_id] 
    
    response = client.post(TASK_URL, json=task_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "is not a valid team member" in response.json()["detail"]

def test_09_update_task_assignment_to_unrelated_user_fails(client, created_project_id, created_owner_id, created_unrelated_user_id):
    """Test PATCH /api/tasks/{task_id} to update assignment to an invalid user (400)."""

    # 1. Create a valid initial task
    create_data = TASK_BASE_CREATE.copy()
    create_data["project_id"] = created_project_id
    create_data["assigned_user_ids"] = [created_owner_id]
    
    create_response = client.post(TASK_URL, json=create_data)
    task_id = create_response.json()["id"]
    
    update_data = {"assigned_user_ids": [created_unrelated_user_id]}
    update_response = client.patch(f"{TASK_URL}{task_id}", json=update_data)
    
    assert update_response.status_code == status.HTTP_400_BAD_REQUEST
    assert "is not a valid team member" in update_response.json()["detail"]
    
    read_response = client.get(f"{TASK_URL}{task_id}")
    assigned_ids = [u["id"] for u in read_response.json()["assigned_users"]]
    assert assigned_ids == [created_owner_id]

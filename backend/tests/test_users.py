import pytest
from fastapi import status

# The 'client' and 'db' fixtures are automatically found from conftest.py

# Data to be used across tests
USER_DATA = {
    "email": "test@example.com",
    "password": "securepassword",
    "full_name": "Test User",
    "is_superuser": False
}
USER_URL = "/api/users/"


def test_create_user(client):
    """Test POST /api/users/ to create a user."""
    response = client.post(USER_URL, json=USER_DATA)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["email"] == USER_DATA["email"]
    assert data["full_name"] == USER_DATA["full_name"]
    # Hashed password should NOT be returned
    assert "hashed_password" not in data


def test_create_user_duplicate_email(client):
    """Test POST /api/users/ for a duplicate email (should fail with 400)."""
    # Create the user first
    client.post(USER_URL, json=USER_DATA)
    
    # Try to create the same user again
    response = client.post(USER_URL, json=USER_DATA)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered."


def test_read_users(client):
    """Test GET /api/users/ to list all users."""
    # Ensure one user exists
    client.post(USER_URL, json=USER_DATA)
    
    response = client.get(USER_URL)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["email"] == USER_DATA["email"]


def test_read_user_by_id(client):
    """Test GET /api/users/{user_id}."""
    # Create user to get an ID
    create_response = client.post(USER_URL, json=USER_DATA)
    user_id = create_response.json()["id"]
    
    response = client.get(f"{USER_URL}{user_id}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == user_id


def test_update_user(client):
    """Test PATCH /api/users/{user_id}."""
    # Create user
    create_response = client.post(USER_URL, json=USER_DATA)
    user_id = create_response.json()["id"]
    
    # Update user's name
    update_data = {"full_name": "Updated Name"}
    response = client.patch(f"{USER_URL}{user_id}", json=update_data)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == "Updated Name"


def test_delete_user(client):
    """Test DELETE /api/users/{user_id}."""
    # Create user
    create_response = client.post(USER_URL, json=USER_DATA)
    user_id = create_response.json()["id"]
    
    # Delete the user
    response = client.delete(f"{USER_URL}{user_id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify the user is gone
    check_response = client.get(f"{USER_URL}{user_id}")
    assert check_response.status_code == status.HTTP_404_NOT_FOUND
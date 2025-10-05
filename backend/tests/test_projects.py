from fastapi import status

PROJECT_URL = "/api/projects/"


def test_01_create_project_success(client, superuser):
    data = {
        "title": "Test Project",
        "description": "Project for testing",
        "owner_id": superuser["id"],
        "collaborator_ids": [],
    }
    resp = client.post(
        PROJECT_URL,
        json=data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["title"] == "Test Project"


def test_02_create_project_owner_is_collaborator_fails(client, superuser):
    data = {
        "title": "Bad Project",
        "description": "Owner cannot be collaborator",
        "owner_id": superuser["id"],
        "collaborator_ids": [superuser["id"]],
    }
    resp = client.post(
        PROJECT_URL,
        json=data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_03_read_project_list(client, superuser):
    resp = client.get(
        PROJECT_URL, headers={"Authorization": f"Bearer {superuser['token']}"}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert isinstance(resp.json(), list)


def test_04_read_project_by_id(client, superuser):
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Read Project",
            "description": "Read by ID",
            "owner_id": superuser["id"],
            "collaborator_ids": [],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]
    resp = client.get(
        f"{PROJECT_URL}{project_id}",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["id"] == project_id


def test_05_update_project_title_and_collaborators(client, superuser):
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Update Project",
            "description": "Before update",
            "owner_id": superuser["id"],
            "collaborator_ids": [],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]
    update_data = {"title": "Updated Title", "collaborator_ids": []}
    resp = client.patch(
        f"{PROJECT_URL}{project_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["title"] == "Updated Title"


def test_06_update_project_collaborators_invalid(client, superuser):
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Invalid Collab Project",
            "description": "Test",
            "owner_id": superuser["id"],
            "collaborator_ids": [],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]
    update_data = {"collaborator_ids": [superuser["id"]]}
    resp = client.patch(
        f"{PROJECT_URL}{project_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_07_delete_project_success(client, superuser):
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Delete Project",
            "description": "To be deleted",
            "owner_id": superuser["id"],
            "collaborator_ids": [],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]
    resp = client.delete(
        f"{PROJECT_URL}{project_id}",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_08_only_owner_can_update_project(client, superuser):
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Owner Check",
            "description": "Owner only update",
            "owner_id": superuser["id"],
            "collaborator_ids": [],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]

    # Create another user
    other_user = client.post(
        "/api/users/",
        json={
            "email": "other@test.com",
            "password": "TestPass123!",
            "full_name": "Other User",
            "is_superuser": False,
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "other@test.com", "password": "TestPass123!"},
    )
    token = login_resp.json()["access_token"]

    update_data = {"title": "Hack Attempt"}
    resp = client.patch(
        f"{PROJECT_URL}{project_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_09_only_owner_can_delete_project(client, superuser):
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Owner Delete Check",
            "description": "Owner only delete",
            "owner_id": superuser["id"],
            "collaborator_ids": [],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]

    other_user = client.post(
        "/api/users/",
        json={
            "email": "other2@test.com",
            "password": "TestPass123!",
            "full_name": "Other2 User",
            "is_superuser": False,
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "other2@test.com", "password": "TestPass123!"},
    )
    token = login_resp.json()["access_token"]

    resp = client.delete(
        f"{PROJECT_URL}{project_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_10_project_with_tags(client, superuser):
    """Test creating and updating project with tags."""
    # Create a tag first
    tag = client.post(
        "/tags/",
        json={"name": "Active", "color": "#00FF00"},
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Create project with tag
    project_data = {
        "title": "Tagged Project",
        "description": "Project with tags",
        "tag_ids": [tag["id"]],
        "owner_id": superuser["id"],
    }
    resp = client.post(
        PROJECT_URL,
        json=project_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert len(data["tags"]) == 1
    assert data["tags"][0]["name"] == "Active"


def test_11_project_history(client, superuser):
    """Test project history creation on updates."""
    # Create project
    project = client.post(
        PROJECT_URL,
        json={
            "title": "History Project",
            "description": "Testing history",
            "owner_id": superuser["id"],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Update project
    resp = client.patch(
        f"{PROJECT_URL}{project['id']}",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK

    # Get project history
    resp = client.get(
        f"{PROJECT_URL}{project['id']}/history",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    history = resp.json()
    assert len(history) > 0
    assert any(h["field_name"] == "title" for h in history)


def test_12_project_timestamps(client, superuser):
    """Test that project timestamps are properly set and updated."""
    # Create project
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Timestamp Project",
            "description": "Testing timestamps",
            "owner_id": superuser["id"],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    assert project["created_at"] is not None
    assert project["updated_at"] is not None
    created_at = project["updated_at"]

    # Update project
    resp = client.patch(
        f"{PROJECT_URL}{project['id']}",
        json={"description": "Updated description"},
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    updated_project = resp.json()
    assert updated_project["updated_at"] > created_at

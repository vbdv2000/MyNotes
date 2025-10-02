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
            "password": "pass",
            "full_name": "Other User",
            "is_superuser": False,
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    other_id = other_user.json()["id"]
    login_resp = client.post(
        "/api/auth/login", data={"username": "other@test.com", "password": "pass"}
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
            "password": "pass",
            "full_name": "Other2 User",
            "is_superuser": False,
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    login_resp = client.post(
        "/api/auth/login", data={"username": "other2@test.com", "password": "pass"}
    )
    token = login_resp.json()["access_token"]

    resp = client.delete(
        f"{PROJECT_URL}{project_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN

from fastapi import status

TASK_URL = "/api/tasks/"
PROJECT_URL = "/api/projects/"


def test_01_create_task_assigned_to_owner(client, superuser):
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Task Project",
            "description": "Project for task",
            "owner_id": superuser["id"],
            "collaborator_ids": [],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]

    task_data = {
        "title": "Owner Task",
        "description": "Assigned to owner",
        "status": "todo",
        "project_id": project_id,
        "assigned_user_ids": [superuser["id"]],
    }
    resp = client.post(
        TASK_URL,
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED


def test_02_create_task_assigned_to_collaborator(client, superuser):
    collab = client.post(
        "/api/users/",
        json={
            "email": "collab@test.com",
            "password": "pass",
            "full_name": "Collaborator",
            "is_superuser": False,
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    collab_id = collab.json()["id"]

    project = client.post(
        PROJECT_URL,
        json={
            "title": "Task Collab Project",
            "description": "Project for collab",
            "owner_id": superuser["id"],
            "collaborator_ids": [collab_id],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]

    task_data = {
        "title": "Collab Task",
        "description": "Assigned to collaborator",
        "status": "todo",
        "project_id": project_id,
        "assigned_user_ids": [collab_id],
    }
    resp = client.post(
        TASK_URL,
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED


def test_03_create_task_assigned_to_multiple_members(client, superuser):
    collab = client.post(
        "/api/users/",
        json={
            "email": "collab2@test.com",
            "password": "pass",
            "full_name": "Collaborator2",
            "is_superuser": False,
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    collab_id = collab.json()["id"]

    project = client.post(
        PROJECT_URL,
        json={
            "title": "Multi Task Project",
            "description": "Project for multiple assignment",
            "owner_id": superuser["id"],
            "collaborator_ids": [collab_id],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]

    task_data = {
        "title": "Multi Task",
        "description": "Assigned to both",
        "status": "todo",
        "project_id": project_id,
        "assigned_user_ids": [superuser["id"], collab_id],
    }
    resp = client.post(
        TASK_URL,
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED


def test_04_create_task_assigned_to_unrelated_user_fails(client, superuser):
    unrelated = client.post(
        "/api/users/",
        json={
            "email": "unrelated@test.com",
            "password": "pass",
            "full_name": "Unrelated",
            "is_superuser": False,
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    unrelated_id = unrelated.json()["id"]

    project = client.post(
        PROJECT_URL,
        json={
            "title": "Unrelated Task Project",
            "description": "Project",
            "owner_id": superuser["id"],
            "collaborator_ids": [],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]

    task_data = {
        "title": "Bad Task",
        "description": "Assigned to unrelated",
        "status": "todo",
        "project_id": project_id,
        "assigned_user_ids": [unrelated_id],
    }
    resp = client.post(
        TASK_URL,
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

from fastapi import status

PROJECT_URL = "/api/projects/"
TAG_URL = "/api/tags/"


def test_01_create_task_assigned_to_owner(client, superuser):
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Task Project",
            "description": "Project for task",
            "collaborator_ids": [],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]

    task_data = {
        "title": "Owner Task",
        "description": "Assigned to owner",
        "status": "todo",
        "assigned_user_ids": [superuser["id"]],
    }
    resp = client.post(
        f"{PROJECT_URL}{project_id}/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED


def test_02_create_task_assigned_to_collaborator(client, superuser):
    collab = client.post(
        "/api/users/",
        json={
            "email": "collab@test.com",
            "password": "TestPass123!",
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
        "assigned_user_ids": [collab_id],
    }
    resp = client.post(
        f"{PROJECT_URL}{project_id}/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED


def test_03_create_task_assigned_to_multiple_members(client, superuser):
    collab = client.post(
        "/api/users/",
        json={
            "email": "collab2@test.com",
            "password": "TestPass123!",
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
        "assigned_user_ids": [superuser["id"], collab_id],
    }
    resp = client.post(
        f"{PROJECT_URL}{project_id}/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED


def test_04_create_task_assigned_to_unrelated_user_fails(client, superuser):
    unrelated = client.post(
        "/api/users/",
        json={
            "email": "unrelated@test.com",
            "password": "TestPass123!",
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
        "assigned_user_ids": [unrelated_id],
    }
    resp = client.post(
        f"{PROJECT_URL}{project_id}/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_05_create_task_with_priority_and_due_date(client, superuser):
    """Test creating a task with priority and due date."""
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Priority Task Project",
            "description": "Project with priority tasks",
            "owner_id": superuser["id"],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    project_id = project.json()["id"]

    task_data = {
        "title": "High Priority Task",
        "description": "Must be done soon",
        "status": "todo",
        "priority": "high",
        "due_date": "2025-12-31T23:59:59",
        "assigned_user_ids": [superuser["id"]],
    }
    resp = client.post(
        f"{PROJECT_URL}{project_id}/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["priority"] == "high"
    assert "2025-12-31" in data["due_date"]


def test_06_update_task_priority(client, superuser):
    """Test updating task priority."""
    project_id = client.post(
        PROJECT_URL,
        json={"title": "Update Priority Project", "description": "Test project"},
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()["id"]

    task = client.post(
        f"{PROJECT_URL}{project_id}/tasks/",
        json={
            "title": "Normal Priority Task",
            "priority": "medium",
            "assigned_user_ids": [superuser["id"]],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    resp = client.put(
        f"{PROJECT_URL}{project_id}/tasks/{task['id']}",
        json={"priority": "urgent"},
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["priority"] == "urgent"


def test_07_task_history_on_update(client, superuser):
    """Test that task history is created on updates."""
    project_id = client.post(
        PROJECT_URL,
        json={"title": "History Test Project", "description": "Test project"},
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()["id"]

    task = client.post(
        f"{PROJECT_URL}{project_id}/tasks/",
        json={
            "title": "Task to Update",
            "status": "todo",
            "assigned_user_ids": [superuser["id"]],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Update status
    client.put(
        f"{PROJECT_URL}{project_id}/tasks/{task['id']}",
        json={"status": "in-progress"},
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )

    # Get task history
    resp = client.get(
        f"{PROJECT_URL}{project_id}/tasks/{task['id']}/history",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    history = resp.json()
    assert len(history) > 0
    assert any(h["field_name"] == "status" for h in history)


def test_08_task_with_tags(client, superuser):
    """Test creating and updating task with tags."""
    # Create a tag first
    tag_resp = client.post(
        TAG_URL,
        json={"name": "Important", "color": "#FF0000"},
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert tag_resp.status_code == status.HTTP_201_CREATED, (
        f"Tag creation failed with status {tag_resp.status_code}. Response: {tag_resp.json()}"
    )
    tag = tag_resp.json()
    project_id = client.post(
        PROJECT_URL,
        json={"title": "Tagged Project", "description": "Test project"},
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()["id"]

    # Create task with tag
    task_data = {
        "title": "Tagged Task",
        "description": "Task with tags",
        "tag_ids": [tag["id"]],
        "assigned_user_ids": [superuser["id"]],
    }
    resp = client.post(
        f"{PROJECT_URL}{project_id}/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert len(data["tags"]) == 1
    assert data["tags"][0]["name"] == "Important"

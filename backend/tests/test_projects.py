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
        "/api/tags/",
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
    print(data)
    assert len(data["tags"]) == 1
    assert data["tags"][0]["name"] == "Active"


def test_11_project_timestamps(client, superuser):
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


def test_12_project_task_creation(client, superuser):
    """Test creating tasks within a project."""
    # Create a project first
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Task Test Project",
            "description": "Project for testing tasks",
            "owner_id": superuser["id"],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Create a task
    task_data = {
        "title": "Test Task",
        "description": "Task in project",
        "status": "todo",
        "priority": "medium",
        "assigned_user_ids": [superuser["id"]],
    }
    resp = client.post(
        f"{PROJECT_URL}{project['id']}/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    task = resp.json()
    assert task["title"] == task_data["title"]
    assert task["project_id"] == project["id"]


def test_13_list_project_tasks(client, superuser):
    """Test listing all tasks in a project."""
    # Create project with multiple tasks
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Multi-task Project",
            "description": "Project with multiple tasks",
            "owner_id": superuser["id"],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Create several tasks
    task_titles = ["Task 1", "Task 2", "Task 3"]
    for title in task_titles:
        client.post(
            f"{PROJECT_URL}{project['id']}/tasks",
            json={
                "title": title,
                "status": "todo",
                "assigned_user_ids": [superuser["id"]],
            },
            headers={"Authorization": f"Bearer {superuser['token']}"},
        )

    # Get tasks list
    resp = client.get(
        f"{PROJECT_URL}{project['id']}/tasks",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    tasks = resp.json()
    assert len(tasks) >= len(task_titles)
    assert all(task["project_id"] == project["id"] for task in tasks)


def test_14_update_project_task(client, superuser):
    """Test updating a task within a project."""
    # Create project and task
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Update Task Project",
            "description": "Project for testing task updates",
            "owner_id": superuser["id"],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    task = client.post(
        f"{PROJECT_URL}{project['id']}/tasks",
        json={
            "title": "Task to Update",
            "status": "todo",
            "assigned_user_ids": [superuser["id"]],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Update task
    update_data = {
        "title": "Updated Task",
        "status": "in-progress",
        "priority": "high",
    }
    resp = client.put(
        f"{PROJECT_URL}{project['id']}/tasks/{task['id']}",
        json=update_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    updated_task = resp.json()
    assert updated_task["title"] == update_data["title"]
    assert updated_task["status"] == update_data["status"]
    assert updated_task["priority"] == update_data["priority"]


def test_15_delete_project_task(client, superuser):
    """Test deleting a task from a project."""
    # Create project and task
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Delete Task Project",
            "description": "Project for testing task deletion",
            "owner_id": superuser["id"],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    task = client.post(
        f"{PROJECT_URL}{project['id']}/tasks",
        json={
            "title": "Task to Delete",
            "status": "todo",
            "assigned_user_ids": [superuser["id"]],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Delete task
    resp = client.delete(
        f"{PROJECT_URL}{project['id']}/tasks/{task['id']}",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    # Verify task is deleted
    resp = client.get(
        f"{PROJECT_URL}{project['id']}/tasks/{task['id']}",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_16_project_pagination(client, superuser):
    """Test project list pagination."""
    # Create multiple projects
    for i in range(5):
        client.post(
            PROJECT_URL,
            json={
                "title": f"Project {i}",
                "description": f"Test project {i}",
                "owner_id": superuser["id"],
            },
            headers={"Authorization": f"Bearer {superuser['token']}"},
        )

    # Test pagination
    resp = client.get(
        f"{PROJECT_URL}?skip=2&limit=2",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    projects = resp.json()
    assert len(projects) == 2


def test_17_task_history_on_update(client, superuser):
    """Test that task history is created on updates."""
    project = client.post(
        PROJECT_URL,
        json={"title": "History Test Project", "description": "Test project"},
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    task = client.post(
        f"{PROJECT_URL}{project['id']}/tasks/",
        json={
            "title": "Task to Update",
            "status": "todo",
            "assigned_user_ids": [superuser["id"]],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Update status
    client.put(
        f"{PROJECT_URL}{project['id']}/tasks/{task['id']}",
        json={"status": "in-progress"},
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )

    # Get task history
    resp = client.get(
        f"{PROJECT_URL}{project['id']}/tasks/{task['id']}/history",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    history = resp.json()
    assert len(history) > 0
    assert any(h["field_name"] == "status" for h in history)


def test_18_task_with_priority_and_due_date(client, superuser):
    """Test creating a task with priority and due date."""
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Priority Task Project",
            "description": "Project with priority tasks",
            "owner_id": superuser["id"],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    task_data = {
        "title": "High Priority Task",
        "description": "Must be done soon",
        "status": "todo",
        "priority": "high",
        "due_date": "2025-12-31T23:59:59",
        "assigned_user_ids": [superuser["id"]],
    }
    resp = client.post(
        f"{PROJECT_URL}{project['id']}/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["priority"] == "high"
    assert "2025-12-31" in data["due_date"]


def test_19_collaborator_task_assignments(client, superuser):
    """Test task assignments for project owner and collaborators."""
    # Create collaborator
    collab = client.post(
        "/api/users/",
        json={
            "email": "collab@test.com",
            "password": "TestPass123!",
            "full_name": "Collaborator",
            "is_superuser": False,
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Get collaborator token
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "collab@test.com", "password": "TestPass123!"},
    )
    collab_token = login_resp.json()["access_token"]

    # Create project with collaborator
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Task Assignment Project",
            "description": "Testing task assignments",
            "owner_id": superuser["id"],
            "collaborator_ids": [collab["id"]],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Owner creates task assigned to self
    owner_task = client.post(
        f"{PROJECT_URL}{project['id']}/tasks/",
        json={
            "title": "Owner Task",
            "status": "todo",
            "assigned_user_ids": [superuser["id"]],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert owner_task.status_code == status.HTTP_201_CREATED

    # Collaborator creates task assigned to self
    collab_task = client.post(
        f"{PROJECT_URL}{project['id']}/tasks/",
        json={
            "title": "Collab Task",
            "status": "todo",
            "assigned_user_ids": [collab["id"]],
        },
        headers={"Authorization": f"Bearer {collab_token}"},
    )
    assert collab_task.status_code == status.HTTP_201_CREATED

    # Owner creates task assigned to both
    multi_task = client.post(
        f"{PROJECT_URL}{project['id']}/tasks/",
        json={
            "title": "Multi-User Task",
            "status": "todo",
            "assigned_user_ids": [superuser["id"], collab["id"]],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert multi_task.status_code == status.HTTP_201_CREATED


def test_20_collaborator_permissions(client, superuser):
    """Test project access and permissions for collaborators."""
    # Create another user as collaborator
    collab = client.post(
        "/api/users/",
        json={
            "email": "collab_test@test.com",
            "password": "TestPass123!",
            "full_name": "Collaborator Test",
            "is_superuser": False,
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Get collaborator token
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "collab_test@test.com", "password": "TestPass123!"},
    )
    collab_token = login_resp.json()["access_token"]

    # Create project with collaborator
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Collab Project",
            "description": "Project with collaborator",
            "owner_id": superuser["id"],
            "collaborator_ids": [collab["id"]],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Collaborator should be able to view the project
    resp = client.get(
        f"{PROJECT_URL}{project['id']}",
        headers={"Authorization": f"Bearer {collab_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK

    # Collaborator should be able to create tasks
    task_resp = client.post(
        f"{PROJECT_URL}{project['id']}/tasks/",
        json={
            "title": "Collab Task",
            "status": "todo",
            "assigned_user_ids": [collab["id"]],
        },
        headers={"Authorization": f"Bearer {collab_token}"},
    )
    assert task_resp.status_code == status.HTTP_201_CREATED

    # But collaborator should not be able to delete the project
    resp = client.delete(
        f"{PROJECT_URL}{project['id']}",
        headers={"Authorization": f"Bearer {collab_token}"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_21_project_list_pagination(client, superuser):
    """Test pagination for the project list."""
    # Create multiple projects
    NUM_PROJECTS = 7
    projects_created = []
    for i in range(NUM_PROJECTS):
        resp = client.post(
            PROJECT_URL,
            json={
                "title": f"Project {i}",
                "description": f"Project {i} for pagination testing",
                "owner_id": superuser["id"],
            },
            headers={"Authorization": f"Bearer {superuser['token']}"},
        )
        assert resp.status_code == status.HTTP_201_CREATED
        projects_created.append(resp.json())

    # Test first page (skip=0, limit=3)
    resp = client.get(
        f"{PROJECT_URL}?skip=0&limit=3",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    first_page = resp.json()
    assert len(first_page) == 3

    # Test middle page (skip=3, limit=3)
    resp = client.get(
        f"{PROJECT_URL}?skip=3&limit=3",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    middle_page = resp.json()
    assert len(middle_page) == 3

    # Test last page (should contain remaining items)
    resp = client.get(
        f"{PROJECT_URL}?skip=6&limit=3",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    last_page = resp.json()
    assert len(last_page) == 1  # Should have only 1 remaining project


def test_22_project_tasks_pagination(client, superuser):
    """Test pagination of tasks within a specific project."""
    # Create a project for task testing
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Project with Paged Tasks",
            "description": "Testing task pagination",
            "owner_id": superuser["id"],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Create multiple tasks
    NUM_TASKS = 7
    for i in range(NUM_TASKS):
        resp = client.post(
            f"{PROJECT_URL}{project['id']}/tasks",
            headers={"Authorization": f"Bearer {superuser['token']}"},
            json={
                "title": f"Task {i}",
                "description": f"Task {i} for pagination testing",
                "status": "todo",
                "priority": "medium",
                "assigned_user_ids": [superuser["id"]],
            },
        )
        assert resp.status_code == status.HTTP_201_CREATED

    # Test first page (skip=0, limit=3)
    resp = client.get(
        f"{PROJECT_URL}{project['id']}/tasks?skip=0&limit=3",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    first_page = resp.json()
    assert len(first_page) == 3
    assert first_page[0]["title"] == "Task 0"

    # Test middle page (skip=3, limit=3)
    resp = client.get(
        f"{PROJECT_URL}{project['id']}/tasks?skip=3&limit=3",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    middle_page = resp.json()
    assert len(middle_page) == 3
    assert middle_page[0]["title"] == "Task 3"

    # Test last page (should contain remaining items)
    resp = client.get(
        f"{PROJECT_URL}{project['id']}/tasks?skip=6&limit=3",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    last_page = resp.json()
    assert len(last_page) == 1  # Should have only 1 remaining task
    assert last_page[0]["title"] == "Task 6"


def test_23_pagination_invalid_params(client, superuser):
    """Test pagination with invalid parameters."""
    # Create a project for testing
    project = client.post(
        PROJECT_URL,
        json={
            "title": "Test Project",
            "description": "Testing invalid pagination",
            "owner_id": superuser["id"],
        },
        headers={"Authorization": f"Bearer {superuser['token']}"},
    ).json()

    # Test negative skip
    resp = client.get(
        f"{PROJECT_URL}?skip=-1&limit=10",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test zero limit
    resp = client.get(
        f"{PROJECT_URL}?skip=0&limit=0",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test too large limit
    resp = client.get(
        f"{PROJECT_URL}?skip=0&limit=1001",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test negative skip for tasks
    resp = client.get(
        f"{PROJECT_URL}{project['id']}/tasks?skip=-1&limit=10",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test zero limit for tasks
    resp = client.get(
        f"{PROJECT_URL}{project['id']}/tasks?skip=0&limit=0",
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

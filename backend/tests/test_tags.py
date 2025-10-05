from fastapi import status
import pytest

TAGS_URL = "/api/tags"


@pytest.fixture
def test_project(client, normal_user_token_headers):
    """Create a test project for tag testing."""
    response = client.post(
        "/api/projects/",
        headers=normal_user_token_headers,
        json={
            "title": "Test Project",
            "description": "For tag testing",
        },
    )
    return response.json()


@pytest.fixture
def test_task(client, normal_user_token_headers, test_project):
    """Create a test task for tag testing."""
    response = client.post(
        f"/api/projects/{test_project['id']}/tasks/",
        headers=normal_user_token_headers,
        json={
            "title": "Test Task",
            "description": "For tags",
            "status": "todo",
        },
    )
    return response.json()


@pytest.fixture
def sample_tag(client, normal_user_token_headers):
    """Create a sample tag for testing."""
    response = client.post(
        TAGS_URL,
        headers=normal_user_token_headers,
        json={"name": "Test Tag", "color": "#FF0000"},
    )
    return response.json()


def test_01_create_tag(client, normal_user_token_headers):
    """Test creating a tag."""
    response = client.post(
        TAGS_URL,
        headers=normal_user_token_headers,
        json={"name": "Important", "color": "#FF0000"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Important"
    assert data["color"] == "#FF0000"
    assert "id" in data
    assert "created_at" in data


def test_02_create_tag_validation(client, normal_user_token_headers):
    """Test tag creation validation."""
    # Test invalid color format
    response = client.post(
        TAGS_URL,
        headers=normal_user_token_headers,
        json={"name": "Bad Color", "color": "red"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Test duplicate name
    client.post(
        TAGS_URL,
        headers=normal_user_token_headers,
        json={"name": "Unique", "color": "#000000"},
    )
    response = client.post(
        TAGS_URL,
        headers=normal_user_token_headers,
        json={"name": "Unique", "color": "#111111"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_03_get_tags_pagination(client, normal_user_token_headers):
    """Test tag list pagination."""
    # Create multiple tags
    tags = [{"name": f"Tag {i}", "color": "#FF0000"} for i in range(5)]
    for tag in tags:
        client.post(TAGS_URL, headers=normal_user_token_headers, json=tag)

    # Test default pagination
    response = client.get(TAGS_URL, headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 5

    # Test custom pagination
    response = client.get(
        f"{TAGS_URL}?skip=2&limit=2", headers=normal_user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) <= 2


def test_04_search_tags(client, normal_user_token_headers):
    """Test searching tags by name."""
    # Create tags with different names
    tags = [
        {"name": "Urgent Bug", "color": "#FF0000"},
        {"name": "Bug Fix", "color": "#00FF00"},
        {"name": "Feature Request", "color": "#0000FF"},
    ]
    for tag in tags:
        client.post(TAGS_URL, headers=normal_user_token_headers, json=tag)

    # Search for tags containing "Bug"
    response = client.get(f"{TAGS_URL}?search=Bug", headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all("Bug" in t["name"] for t in data)


def test_05_update_tag(client, normal_user_token_headers, sample_tag):
    """Test updating a tag."""
    update_data = {"name": "Updated Name", "color": "#FFFFFF"}
    response = client.put(
        f"{TAGS_URL}/{sample_tag['id']}",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["color"] == update_data["color"]


def test_06_partial_update_tag(client, normal_user_token_headers, sample_tag):
    """Test partial update of a tag."""
    # Update only the color
    response = client.put(
        f"{TAGS_URL}/{sample_tag['id']}",
        headers=normal_user_token_headers,
        json={"color": "#00FF00"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == sample_tag["name"]  # Name should not change
    assert data["color"] == "#00FF00"  # Color should update


def test_07_delete_tag(client, normal_user_token_headers, sample_tag):
    """Test deleting a tag."""
    response = client.delete(
        f"{TAGS_URL}/{sample_tag['id']}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's gone
    response = client.get(
        f"{TAGS_URL}/{sample_tag['id']}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_08_get_tasks_by_tag(client, normal_user_token_headers, test_task, sample_tag):
    """Test getting tasks that have a specific tag."""
    # Assign tag to task
    client.put(
        f"/api/projects/{test_task['project_id']}/tasks/{test_task['id']}",
        headers=normal_user_token_headers,
        json={"tag_ids": [sample_tag["id"]]},
    )

    # Get tasks with tag
    response = client.get(
        f"{TAGS_URL}/{sample_tag['id']}/tasks",
        headers=normal_user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(t["id"] == test_task["id"] for t in data)


def test_09_tag_count(client, normal_user_token_headers):
    """Test getting total tag count."""
    # Create some tags
    for i in range(3):
        client.post(
            TAGS_URL,
            headers=normal_user_token_headers,
            json={"name": f"Count Tag {i}", "color": "#000000"},
        )

    response = client.get(f"{TAGS_URL}/count", headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert data["total"] >= 3


def test_10_error_cases(client, normal_user_token_headers):
    """Test various error cases."""
    # Test invalid tag ID
    response = client.get(f"{TAGS_URL}/99999", headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Test invalid color format in update
    response = client.put(
        f"{TAGS_URL}/1",
        headers=normal_user_token_headers,
        json={"color": "invalid-color"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Test duplicate name in update
    tag1 = client.post(
        TAGS_URL,
        headers=normal_user_token_headers,
        json={"name": "Original", "color": "#000000"},
    ).json()

    tag2 = client.post(
        TAGS_URL,
        headers=normal_user_token_headers,
        json={"name": "Second", "color": "#111111"},
    ).json()

    response = client.put(
        f"{TAGS_URL}/{tag2['id']}",
        headers=normal_user_token_headers,
        json={"name": "Original"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

from fastapi import status

USER_URL = "/api/users/"

def test_01_create_user_success(client, superuser):
    user_data = {
        "email": "user1@test.com",
        "password": "testpass",
        "full_name": "User One",
        "is_superuser": False
    }
    resp = client.post(USER_URL, json=user_data, headers={"Authorization": f"Bearer {superuser['token']}"})
    assert resp.status_code == status.HTTP_201_CREATED
    assert "id" in resp.json()

def test_02_create_user_duplicate_email_fails(client, superuser):
    user_data = {
        "email": "user2@test.com",
        "password": "testpass",
        "full_name": "User Two",
        "is_superuser": False
    }
    client.post(USER_URL, json=user_data, headers={"Authorization": f"Bearer {superuser['token']}"})
    resp = client.post(USER_URL, json=user_data, headers={"Authorization": f"Bearer {superuser['token']}"})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

def test_03_read_user_by_id_success(client, superuser):
    user = client.post(USER_URL, json={
        "email": "user3@test.com",
        "password": "testpass",
        "full_name": "User Three",
        "is_superuser": False
    }, headers={"Authorization": f"Bearer {superuser['token']}"})
    user_id = user.json()["id"]
    resp = client.get(f"{USER_URL}{user_id}", headers={"Authorization": f"Bearer {superuser['token']}"})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["id"] == user_id

def test_04_read_user_by_id_not_found(client, superuser):
    resp = client.get(f"{USER_URL}9999", headers={"Authorization": f"Bearer {superuser['token']}"})
    assert resp.status_code == status.HTTP_404_NOT_FOUND

def test_05_update_user_success(client, superuser):
    user = client.post(USER_URL, json={
        "email": "user4@test.com",
        "password": "testpass",
        "full_name": "User Four",
        "is_superuser": False
    }, headers={"Authorization": f"Bearer {superuser['token']}"})
    user_id = user.json()["id"]
    update_data = {"full_name": "Updated User Four"}
    resp = client.patch(f"{USER_URL}{user_id}", json=update_data, headers={"Authorization": f"Bearer {superuser['token']}"})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["full_name"] == "Updated User Four"

def test_06_update_user_not_found(client, superuser):
    resp = client.patch(f"{USER_URL}9999", json={"full_name": "No User"}, headers={"Authorization": f"Bearer {superuser['token']}"})
    assert resp.status_code == status.HTTP_404_NOT_FOUND

def test_07_delete_user_success(client, superuser):
    user = client.post(USER_URL, json={
        "email": "user5@test.com",
        "password": "testpass",
        "full_name": "User Five",
        "is_superuser": False
    }, headers={"Authorization": f"Bearer {superuser['token']}"})
    user_id = user.json()["id"]
    resp = client.delete(f"{USER_URL}{user_id}", headers={"Authorization": f"Bearer {superuser['token']}"})
    assert resp.status_code == status.HTTP_204_NO_CONTENT

def test_08_delete_user_not_found(client, superuser):
    resp = client.delete(f"{USER_URL}9999", headers={"Authorization": f"Bearer {superuser['token']}"})
    assert resp.status_code == status.HTTP_404_NOT_FOUND

def test_09_read_users_list(client, superuser):
    resp = client.get(USER_URL, headers={"Authorization": f"Bearer {superuser['token']}"})
    assert resp.status_code == status.HTTP_200_OK

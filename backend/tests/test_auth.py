from fastapi import status

USER_URL = "/api/users/"
LOGIN_URL = "/api/auth/login"


def test_01_login_success(client, superuser):
    user_data = {
        "email": "authuser@test.com",
        "password": "TestPass123!",
        "full_name": "Auth User",
        "is_superuser": False,
    }
    client.post(
        USER_URL,
        json=user_data,
        headers={"Authorization": f"Bearer {superuser['token']}"},
    )

    resp = client.post(
        LOGIN_URL, data={"username": "authuser@test.com", "password": "TestPass123!"}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert "access_token" in resp.json()


def test_02_login_fail_wrong_credentials(client):
    resp = client.post(
        LOGIN_URL, data={"username": "wrong@test.com", "password": "badpass"}
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_03_login_fail_missing_fields(client):
    resp = client.post(LOGIN_URL, data={"username": "authuser@test.com"})
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

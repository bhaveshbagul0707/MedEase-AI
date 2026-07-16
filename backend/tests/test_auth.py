import pytest


@pytest.mark.asyncio
async def test_register_success(client, register_payload):
    response = await client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["access_token"]
    assert data["data"]["refresh_token"]
    assert data["data"]["user"]["email"] == register_payload["email"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client, register_payload):
    await client.post("/api/v1/auth/register", json=register_payload)
    response = await client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_password_mismatch(client, register_payload):
    register_payload["confirm_password"] = "DifferentPass123"
    response = await client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client, register_payload):
    await client.post("/api/v1/auth/register", json=register_payload)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
    )
    assert response.status_code == 200
    assert response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(client, register_payload):
    await client.post("/api/v1/auth/register", json=register_payload)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": register_payload["email"], "password": "WrongPassword123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client, register_payload):
    reg = await client.post("/api/v1/auth/register", json=register_payload)
    token = reg.json()["data"]["access_token"]
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["full_name"] == register_payload["full_name"]


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client, register_payload):
    reg = await client.post("/api/v1/auth/register", json=register_payload)
    refresh_token = reg.json()["data"]["refresh_token"]
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_forgot_and_reset_password(client, register_payload):
    await client.post("/api/v1/auth/register", json=register_payload)
    forgot = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": register_payload["email"]},
    )
    assert forgot.status_code == 200
    reset_token = forgot.json()["data"]["reset_token"]
    assert reset_token

    reset = await client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": reset_token,
            "password": "NewSecurePass123",
            "confirm_password": "NewSecurePass123",
        },
    )
    assert reset.status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": register_payload["email"], "password": "NewSecurePass123"},
    )
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_update_profile(client, register_payload):
    reg = await client.post("/api/v1/auth/register", json=register_payload)
    token = reg.json()["data"]["access_token"]
    response = await client.patch(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated Name", "year_of_study": 3},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["full_name"] == "Updated Name"
    assert data["year_of_study"] == 3


@pytest.mark.asyncio
async def test_change_password(client, register_payload):
    reg = await client.post("/api/v1/auth/register", json=register_payload)
    token = reg.json()["data"]["access_token"]
    response = await client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": register_payload["password"],
            "new_password": "NewSecurePass123",
            "confirm_password": "NewSecurePass123",
        },
    )
    assert response.status_code == 200

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": register_payload["email"], "password": "NewSecurePass123"},
    )
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_logout(client, register_payload):
    reg = await client.post("/api/v1/auth/register", json=register_payload)
    token = reg.json()["data"]["access_token"]
    response = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

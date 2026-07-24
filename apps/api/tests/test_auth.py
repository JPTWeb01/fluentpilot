async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_register_login_refresh_me_flow(client):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "learner@example.com", "password": "correct-horse-battery"},
    )
    assert register_resp.status_code == 201
    tokens = register_resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    duplicate_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "learner@example.com", "password": "correct-horse-battery"},
    )
    assert duplicate_resp.status_code == 409

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "learner@example.com", "password": "correct-horse-battery"},
    )
    assert login_resp.status_code == 200
    login_tokens = login_resp.json()

    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login_tokens['access_token']}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "learner@example.com"

    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    assert refresh_resp.status_code == 200
    assert refresh_resp.json()["refresh_token"] != login_tokens["refresh_token"]

    # Refresh tokens rotate on use — the old one must no longer be valid.
    reuse_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    assert reuse_resp.status_code == 401


async def test_login_wrong_password(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpass@example.com", "password": "correct-horse-battery"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "not-the-password"},
    )
    assert resp.status_code == 401


async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)

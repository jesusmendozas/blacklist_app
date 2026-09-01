VALID_UUID = "123e4567-e89b-12d3-a456-426614174000"


def test_ping_no_auth_required(client):
    resp = client.get("/blacklists/ping")
    assert resp.status_code == 200
    assert resp.get_json() == {"message": "pong"}


def test_create_blacklist_success(client, auth_headers):
    resp = client.post(
        "/blacklists",
        json={"email": "user@example.com", "app_uuid": VALID_UUID, "blocked_reason": "Spam"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["email"] == "user@example.com"
    assert "id" in body


def test_create_blacklist_without_auth(client):
    resp = client.post(
        "/blacklists",
        json={"email": "user@example.com", "app_uuid": VALID_UUID},
    )
    assert resp.status_code == 401


def test_create_blacklist_no_body(client, auth_headers):
    resp = client.post("/blacklists", headers=auth_headers)
    assert resp.status_code in (400, 415)


def test_create_blacklist_invalid_data(client, auth_headers):
    resp = client.post(
        "/blacklists",
        json={"email": "not-an-email", "app_uuid": "bad-uuid"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert "details" in body


def test_create_blacklist_duplicate_returns_conflict(client, auth_headers):
    payload = {"email": "dup@example.com", "app_uuid": VALID_UUID}
    first = client.post("/blacklists", json=payload, headers=auth_headers)
    assert first.status_code == 201

    second = client.post("/blacklists", json=payload, headers=auth_headers)
    assert second.status_code == 409


def test_check_blacklist_found(client, auth_headers):
    client.post(
        "/blacklists",
        json={"email": "blocked@example.com", "app_uuid": VALID_UUID, "blocked_reason": "Spam"},
        headers=auth_headers,
    )
    resp = client.get("/blacklists/blocked@example.com", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["is_blacklisted"] is True
    assert body["blocked_reason"] == "Spam"


def test_check_blacklist_not_found(client, auth_headers):
    resp = client.get("/blacklists/nobody@example.com", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["is_blacklisted"] is False


def test_check_blacklist_without_auth(client):
    resp = client.get("/blacklists/user@example.com")
    assert resp.status_code == 401
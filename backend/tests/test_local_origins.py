import os


def test_explicit_local_addresses_and_reject_external(client, monkeypatch):
    monkeypatch.delenv("APP_ORIGIN", raising=False)
    monkeypatch.delenv("APP_ORIGINS", raising=False)
    for origin in (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ):
        result = client.post(
            "/api/login",
            headers={"Origin": origin},
            json={"username": "owner", "password": os.environ["DEMO_PASSWORD"]},
        )
        assert result.status_code == 200
    result = client.post("/api/logout", headers={"Origin": "https://evil.example"})
    assert result.status_code == 403
    assert "detail" in result.json()


def test_configured_origin_does_not_allow_local_fallback(client, monkeypatch):
    monkeypatch.delenv("APP_ORIGINS", raising=False)
    monkeypatch.setenv("APP_ORIGIN", "https://mizan.example")
    assert (
        client.post(
            "/api/login",
            headers={"Origin": "http://127.0.0.1:5174"},
            json={"username": "owner", "password": os.environ["DEMO_PASSWORD"]},
        ).status_code
        == 403
    )

import pytest
from fastapi.testclient import TestClient


def make_client(monkeypatch):
    """Return a TestClient with valid env vars set."""
    monkeypatch.setenv("VAPI_PUBLIC_KEY", "test-public-key")
    monkeypatch.setenv("ASSISTANT_ID", "test-assistant-id")
    from main import app
    return TestClient(app)


def test_health_returns_200(monkeypatch):
    client = make_client(monkeypatch)
    with client:
        response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["config_loaded"] is True
    assert "version" in data


def test_config_returns_keys(monkeypatch):
    client = make_client(monkeypatch)
    with client:
        response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert data["publicKey"] == "test-public-key"
    assert data["assistantId"] == "test-assistant-id"


def test_startup_fails_without_env_vars(monkeypatch):
    monkeypatch.delenv("VAPI_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("ASSISTANT_ID", raising=False)
    from main import app
    with pytest.raises(RuntimeError, match="Missing required environment variables"):
        with TestClient(app):
            pass


def test_root_serves_html(monkeypatch):
    client = make_client(monkeypatch)
    with client:
        response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

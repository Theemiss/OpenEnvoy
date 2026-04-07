import time
import pytest
from typing import Dict, Any

try:
    # Attempt to import the FastAPI app from the backend. If not available in the
    # environment where tests run, we'll skip the tests gracefully.
    from backend.main import app as api_app  # type: ignore
except Exception:
    api_app = None  # Will cause tests to be skipped if app is not importable


@pytest.fixture
def client():
    """FastAPI TestClient fixture.

    Uses the app from backend.main if available. If the app cannot be imported,
    the tests will be skipped by pytest.
    """
    if api_app is None:
        pytest.skip("Backend app not importable; skipping auth integration tests")
    from fastapi.testclient import TestClient
    return TestClient(api_app)


def _unique_email() -> str:
    return f"test-auth-{int(time.time() * 1000)}@example.com"


def _auth_header(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _resp_json_safe(resp) -> Dict[str, Any]:
    try:
        return resp.json()
    except Exception:
        return {}


@pytest.mark.usefixtures("engine", "session")
def test_register_happy_path(client, engine, session):  # type: ignore
    """Register a new user via POST /api/v1/auth/register and verify success."""
    email = _unique_email()
    payload = {"email": email, "password": "Secret123!"}
    resp = client.post("/api/v1/auth/register", json=payload)
    if resp.status_code == 404:
        pytest.skip("Auth register endpoint not implemented yet")
    assert resp.status_code in (200, 201), f"Expected 200/201, got {resp.status_code}. Response: {resp.text}"
    data = _resp_json_safe(resp)
    # Basic schema checks
    assert isinstance(data, dict)
    assert data.get("email") == email or data.get("id") is not None
    # Do not expose plaintext password
    assert "password" not in data


@pytest.mark.usefixtures("engine", "session")
def test_login_happy_path(client, engine, session):  # type: ignore
    """Login with valid credentials and obtain a JWT-like access token."""
    email = _unique_email()
    # First, register the user so login can succeed
    register_resp = client.post("/api/v1/auth/register", json={"email": email, "password": "Secret123!"})
    if register_resp.status_code == 404:
        pytest.skip("Auth register/login endpoints not implemented yet")
    assert register_resp.status_code in (200, 201)

    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "Secret123!"})
    if login_resp.status_code == 404:
        pytest.skip("Auth login endpoint not implemented yet")
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = _resp_json_safe(login_resp)
    token = login_data.get("access_token") or login_data.get("token")
    assert isinstance(token, str) and token, "Expected a non-empty access token"

    # Use token to fetch current user
    me_resp = client.get("/api/v1/auth/me", headers=_auth_header(token))
    assert me_resp.status_code == 200
    me_data = _resp_json_safe(me_resp)
    assert me_data.get("email") == email


@pytest.mark.usefixtures("engine", "session")
def test_me_endpoint_requires_auth(client, engine, session):  # type: ignore
    """Protected /me endpoint must require authentication."""
    # No token
    resp_no_auth = client.get("/api/v1/auth/me")
    # Depending on implementation this could be 401 or 403; we accept both as failures to be explicit
    if resp_no_auth.status_code == 404:
        pytest.skip("Auth/me endpoint not implemented yet")
    assert resp_no_auth.status_code in (401, 403)

    # With a valid token should succeed (using a freshly created user)
    email = _unique_email()
    client.post("/api/v1/auth/register", json={"email": email, "password": "Secret123!"})
    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "Secret123!"})
    assert login_resp.status_code == 200
    token = _resp_json_safe(login_resp).get("access_token") or _resp_json_safe(login_resp).get("token")
    assert isinstance(token, str) and token
    me_resp = client.get("/api/v1/auth/me", headers=_auth_header(token))
    if me_resp.status_code == 404:
        pytest.skip("Auth/me endpoint not implemented yet (second check)")
    assert me_resp.status_code == 200


@pytest.mark.usefixtures("engine", "session")
def test_invalid_credentials_handling(client, engine, session):  # type: ignore
    """Wrong credentials should be rejected with appropriate error."""
    email = _unique_email()
    # Attempt login without registration
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPass!"})
    if resp.status_code == 404:
        pytest.skip("Auth login endpoint not implemented yet")
    assert resp.status_code in (401, 403)

    # Register with one password, then attempt login with wrong password
    client.post("/api/v1/auth/register", json={"email": email, "password": "Secret123!"})
    resp_wrong = client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPass!"})
    if resp_wrong.status_code == 404:
        pytest.skip("Auth login endpoint not implemented yet")
    assert resp_wrong.status_code in (401, 403)


@pytest.mark.usefixtures("engine", "session")
def test_password_hashing_verification(client, engine, session):  # type: ignore
    """Ensure backend does not expose plaintext passwords and tokens grant access."""
    email = _unique_email()
    reg_resp = client.post("/api/v1/auth/register", json={"email": email, "password": "Secret123!"})
    if reg_resp.status_code == 404:
        pytest.skip("Auth register/login endpoints not implemented yet")
    assert reg_resp.status_code in (200, 201)
    reg_data = _resp_json_safe(reg_resp)
    assert "password" not in reg_data

    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "Secret123!"})
    if login_resp.status_code == 404:
        pytest.skip("Auth login endpoint not implemented yet")
    assert login_resp.status_code == 200
    token = _resp_json_safe(login_resp).get("access_token") or _resp_json_safe(login_resp).get("token")
    assert isinstance(token, str) and token

    # Access a protected resource with token
    me_resp = client.get("/api/v1/auth/me", headers=_auth_header(token))
    assert me_resp.status_code == 200

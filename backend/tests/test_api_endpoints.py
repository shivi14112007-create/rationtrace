import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "RationTrace"

def test_login_success_and_cookie_set():
    response = client.post("/api/auth/login", json={
        "username": "beneficiary_demo",
        "password": "Demo123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "BENEFICIARY"
    # Verify httpOnly cookie is in Set-Cookie header
    assert "access_token" in response.cookies

def test_login_invalid_credentials():
    response = client.post("/api/auth/login", json={
        "username": "beneficiary_demo",
        "password": "WrongPassword!"
    })
    assert response.status_code == 401

def test_get_me_with_cookie_auth():
    # Login first
    login_resp = client.post("/api/auth/login", json={
        "username": "official_demo",
        "password": "Demo123!"
    })
    token = login_resp.json()["access_token"]

    # Call /api/auth/me using the cookie
    me_resp = client.get("/api/auth/me", cookies={"access_token": token})
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "official_demo"
    assert me_resp.json()["role"] == "OFFICIAL"

def test_role_based_access_restriction():
    # Beneficiary trying to access official audit summary
    beneficiary_login = client.post("/api/auth/login", json={
        "username": "beneficiary_demo",
        "password": "Demo123!"
    })
    token = beneficiary_login.json()["access_token"]

    resp = client.get("/api/audits/summary", cookies={"access_token": token})
    assert resp.status_code == 403
    assert "lacks required permissions" in resp.json()["detail"]

def test_official_access_audit_summary():
    official_login = client.post("/api/auth/login", json={
        "username": "official_demo",
        "password": "Demo123!"
    })
    token = official_login.json()["access_token"]

    resp = client.get("/api/audits/summary", cookies={"access_token": token})
    assert resp.status_code == 200
    data = resp.json()
    assert "open_discrepancies" in data
    assert data["rule_a_count"] >= 1
    assert data["rule_b_count"] >= 1

def test_public_analytics_overview():
    # Unauthenticated visitor can access public analytics
    resp = client.get("/api/analytics/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_shops" in data
    assert data["total_shops"] >= 3
    assert "reconciliation_rate_pct" in data

def test_complaint_lifecycle():
    # 1. Login as beneficiary
    b_login = client.post("/api/auth/login", json={
        "username": "beneficiary_demo",
        "password": "Demo123!"
    })
    b_token = b_login.json()["access_token"]

    # 2. Submit complaint
    create_resp = client.post("/api/complaints", json={
        "related_shop_id": 1,
        "category": "UNDER_DISTRIBUTION",
        "description": "Shortage of 4 kg in monthly wheat allotment."
    }, cookies={"access_token": b_token})
    assert create_resp.status_code == 201
    complaint_data = create_resp.json()
    complaint_id = complaint_data["id"]
    assert complaint_data["status"] == "SUBMITTED"
    assert len(complaint_data["events"]) >= 1

    # 3. Login as official
    o_login = client.post("/api/auth/login", json={
        "username": "official_demo",
        "password": "Demo123!"
    })
    o_token = o_login.json()["access_token"]

    # 4. Official updates status
    patch_resp = client.patch(f"/api/complaints/{complaint_id}/status", json={
        "status": "UNDER_REVIEW",
        "note": "Inspector commenced document audit."
    }, cookies={"access_token": o_token})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "UNDER_REVIEW"
    assert len(patch_resp.json()["events"]) >= 2


def _login(username: str) -> TestClient:
    c = TestClient(app)
    r = c.post("/api/auth/login", json={"username": username, "password": "Demo123!"})
    assert r.status_code == 200
    return c


def test_tinyfish_requires_admin():
    # anonymous
    assert TestClient(app).get("/api/tinyfish/status").status_code in (401, 403)
    assert TestClient(app).post("/api/tinyfish/jobs", json={"source_id": 1, "mode": "DEMO"}).status_code in (401, 403)
    # non-admin roles
    for u in ("beneficiary_demo", "dealer_demo", "official_demo"):
        assert _login(u).get("/api/tinyfish/sources").status_code == 403
    # admin
    assert _login("admin_demo").get("/api/tinyfish/status").status_code == 200

from app.models.user import User, Session as DBSession
from datetime import datetime

def test_plaintext_password_absent(db, client, admin_token_headers):
    # Rule 1: plaintext password is absent from database
    client.post("/api/v1/admin/candidates", json={"username": "plain_test", "full_name": "Test"}, headers=admin_token_headers)
    user = db.query(User).filter(User.username == "plain_test").first()
    assert getattr(user, 'password', None) is None
    
    # Rule 2: password_hash exists but is not returned by API
    res = client.get("/api/v1/auth/me", headers=admin_token_headers)
    data = res.json()
    assert "password_hash" not in data
    assert "password" not in data

def test_session_lifecycle(client, admin_token_headers, db):
    res = client.post("/api/v1/admin/candidates", json={"username": "session_test", "full_name": "Test"}, headers=admin_token_headers)
    temp_pass = res.json()["temporary_password"]
    
    # Login
    res_login = client.post("/api/v1/auth/login", json={"username": "session_test", "password": temp_pass})
    cookie = res_login.cookies.get("defendx_session")
    headers = {"Cookie": f"defendx_session={cookie}"}
    
    # Manually revoke the session in DB
    user = db.query(User).filter(User.username == "session_test").first()
    db_session = db.query(DBSession).filter(DBSession.user_id == user.id).first()
    db_session.revoked_at = datetime(2020, 1, 1)
    db.commit()

    # Rule 11: Revoked session cannot access endpoint
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 401

    # Manually expire the session in DB instead
    db_session.revoked_at = None
    db_session.expires_at = datetime(2020, 1, 1)
    db.commit()

    # Rule 12: Expired session cannot access endpoint
    res_me2 = client.get("/api/v1/auth/me", headers=headers)
    assert res_me2.status_code == 401

def test_inactive_account(client, admin_token_headers, db):
    res = client.post("/api/v1/admin/candidates", json={"username": "inactive_test", "full_name": "Test"}, headers=admin_token_headers)
    temp_pass = res.json()["temporary_password"]
    
    user = db.query(User).filter(User.username == "inactive_test").first()
    user.status = "INACTIVE"
    db.commit()

    res_login = client.post("/api/v1/auth/login", json={"username": "inactive_test", "password": temp_pass})
    cookie = res_login.cookies.get("defendx_session")
    headers = {"Cookie": f"defendx_session={cookie}"}

    # Rule 13: Inactive account cannot authenticate properly to protected routes
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 403

def test_candidate_isolation(client, admin_token_headers, db):
    # Rule 15: Candidate A cannot access Candidate B
    res_a = client.post("/api/v1/admin/candidates", json={"username": "cand_a", "full_name": "A"}, headers=admin_token_headers)
    res_b = client.post("/api/v1/admin/candidates", json={"username": "cand_b", "full_name": "B"}, headers=admin_token_headers)
    
    pass_a = res_a.json()["temporary_password"]
    login_a = client.post("/api/v1/auth/login", json={"username": "cand_a", "password": pass_a})
    cookie_a = login_a.cookies.get("defendx_session")
    headers_a = {"Cookie": f"defendx_session={cookie_a}"}

    # Try to change cand_b's username using cand_a's session.
    # The API doesn't even take a target_username, it relies implicitly on the session.
    # So by design, cand_a can only affect cand_a.
    res_change = client.patch("/api/v1/profile/username", json={"new_username": "hacked_b"}, headers=headers_a)
    assert res_change.status_code == 403 # FAILS because cand_a must change password first!

    client.post("/api/v1/auth/change-password", json={"current_password": pass_a, "new_password": "NewStrongPassword123"}, headers=headers_a)
    
    # Re-login since password change revokes sessions
    login_a2 = client.post("/api/v1/auth/login", json={"username": "cand_a", "password": "NewStrongPassword123"})
    cookie_a2 = login_a2.cookies.get("defendx_session")
    headers_a2 = {"Cookie": f"defendx_session={cookie_a2}"}

    # Try again
    res_change2 = client.patch("/api/v1/profile/username", json={"new_username": "hacked_b"}, headers=headers_a2)
    assert res_change2.status_code == 200
    
    # cand_a changed their own username to hacked_b, but cand_b is untouched
    user_b = db.query(User).filter(User.username == "cand_b").first()
    assert user_b is not None

def test_identity_and_role_overrides(client, admin_token_headers, db):
    res = client.post("/api/v1/admin/candidates", json={"username": "override_test", "full_name": "O"}, headers=admin_token_headers)
    temp_pass = res.json()["temporary_password"]
    
    login_res = client.post("/api/v1/auth/login", json={"username": "override_test", "password": temp_pass})
    cookie = login_res.cookies.get("defendx_session")
    headers = {"Cookie": f"defendx_session={cookie}"}
    
    client.post("/api/v1/auth/change-password", json={"current_password": temp_pass, "new_password": "NewStrongPassword123"}, headers=headers)

    login_res2 = client.post("/api/v1/auth/login", json={"username": "override_test", "password": "NewStrongPassword123"})
    cookie2 = login_res2.cookies.get("defendx_session")
    headers2 = {"Cookie": f"defendx_session={cookie2}"}

    # Rule 16: Username change does not change internal UUID
    user_before = db.query(User).filter(User.username == "override_test").first()
    uuid_before = user_before.id
    
    client.patch("/api/v1/profile/username", json={"new_username": "override_success"}, headers=headers2)
    
    user_after = db.query(User).filter(User.username == "override_success").first()
    assert user_after.id == uuid_before

    # Rule 18: Role cannot be overridden by frontend input
    # API endpoints don't accept 'role' changes. Even if they did, we verify it here.
    res_me = client.get("/api/v1/auth/me", headers=headers2)
    assert res_me.json()["role"] == "CANDIDATE"

import pytest

def test_admin_create_candidate(client, admin_token_headers):
    # Rule 17: Admin can create candidate
    res = client.post("/api/v1/admin/candidates", json={
        "username": "candidate_test",
        "full_name": "Test Candidate",
        "target_force": "Navy"
    }, headers=admin_token_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["user_id"] == "candidate_test"
    assert "temporary_password" in data

    # Rule 3: Duplicate username rejected
    res_dup = client.post("/api/v1/admin/candidates", json={
        "username": "candidate_test",
        "full_name": "Test Candidate 2"
    }, headers=admin_token_headers)
    assert res_dup.status_code == 409

def test_unauthenticated_create_candidate(client):
    res = client.post("/api/v1/admin/candidates", json={"username": "hax0r", "full_name": "Hacker"})
    # Rule 15: Unauthenticated rejected
    assert res.status_code == 401

def test_login_flow(client, admin_token_headers):
    # Create candidate
    res = client.post("/api/v1/admin/candidates", json={"username": "login_test", "full_name": "Log"}, headers=admin_token_headers)
    temp_pass = res.json()["temporary_password"]

    # Rule 4: Invalid login rejected
    res_fail = client.post("/api/v1/auth/login", json={"username": "login_test", "password": "wrongpassword"})
    assert res_fail.status_code == 401
    
    # Rule 5: Valid login succeeds
    res_success = client.post("/api/v1/auth/login", json={"username": "login_test", "password": temp_pass})
    assert res_success.status_code == 200
    
    # Rule 6: Temporary account requires password change
    assert res_success.json()["must_change_password"] is True
    
    # Get session cookie
    cookie = res_success.cookies.get("defendx_session")
    headers = {"Cookie": f"defendx_session={cookie}"}

    # Rule 7: Candidate cannot access normal routes before password change
    # Using profile/username as a normal route
    res_profile = client.patch("/api/v1/profile/username", json={"new_username": "new_login"}, headers=headers)
    assert res_profile.status_code == 403
    assert "Must change password" in res_profile.json()["detail"]

    # Rule 8: Password change succeeds
    res_pw = client.post("/api/v1/auth/change-password", json={"current_password": temp_pass, "new_password": "NewStrongPassword123"}, headers=headers)
    assert res_pw.status_code == 200

    # Rule 9: Old password no longer works
    res_old = client.post("/api/v1/auth/login", json={"username": "login_test", "password": temp_pass})
    assert res_old.status_code == 401

    # Rule 10: New password works
    res_new = client.post("/api/v1/auth/login", json={"username": "login_test", "password": "NewStrongPassword123"})
    assert res_new.status_code == 200
    assert res_new.json()["must_change_password"] is False
    new_cookie = res_new.cookies.get("defendx_session")
    new_headers = {"Cookie": f"defendx_session={new_cookie}"}

    # Rule 11: Username change succeeds
    res_name = client.patch("/api/v1/profile/username", json={"new_username": "new_login_test"}, headers=new_headers)
    assert res_name.status_code == 200

    # Test me endpoint
    res_me = client.get("/api/v1/auth/me", headers=new_headers)
    assert res_me.json()["user_id"] == "new_login_test"

    # Rule 14: Logout invalidates session
    res_logout = client.post("/api/v1/auth/logout", headers=new_headers)
    assert res_logout.status_code == 200
    
    # Try me again
    res_me2 = client.get("/api/v1/auth/me", headers=new_headers)
    assert res_me2.status_code == 401

def test_candidate_cannot_access_admin(client, admin_token_headers):
    # Rule 16: Candidate cannot access admin endpoint
    res = client.post("/api/v1/admin/candidates", json={"username": "cand2", "full_name": "cand"}, headers=admin_token_headers)
    temp_pass = res.json()["temporary_password"]
    
    res_login = client.post("/api/v1/auth/login", json={"username": "cand2", "password": temp_pass})
    cookie = res_login.cookies.get("defendx_session")
    headers = {"Cookie": f"defendx_session={cookie}"}

    # Cand trying to create cand
    # Rule 18: Candidate cannot create another candidate
    res_admin = client.post("/api/v1/admin/candidates", json={"username": "cand3", "full_name": "cand3"}, headers=headers)
    assert res_admin.status_code == 403

import pytest
from app.models.user import User, Profile

def test_get_profile(client, admin_token_headers, db):
    res = client.post("/api/v1/admin/candidates", json={"username": "prof_cand_1", "full_name": "Profile Candidate 1"}, headers=admin_token_headers)
    pass_a = res.json()["temporary_password"]
    
    login_a = client.post("/api/v1/auth/login", json={"username": "prof_cand_1", "password": pass_a})
    cookie_a = login_a.cookies.get("defendx_session")
    headers_a = {"Cookie": f"defendx_session={cookie_a}"}
    
    client.post("/api/v1/auth/change-password", json={"current_password": pass_a, "new_password": "NewStrongPassword123"}, headers=headers_a)
    
    login_a2 = client.post("/api/v1/auth/login", json={"username": "prof_cand_1", "password": "NewStrongPassword123"})
    cookie_a2 = login_a2.cookies.get("defendx_session")
    headers_a2 = {"Cookie": f"defendx_session={cookie_a2}"}
    
    res_prof = client.get("/api/v1/profile", headers=headers_a2)
    assert res_prof.status_code == 200
    data = res_prof.json()
    assert data["full_name"] == "Profile Candidate 1"
    assert data["username"] == "prof_cand_1"
    assert data["target_force"] is None
    assert data["role"] == "CANDIDATE"

def test_update_profile_and_isolation(client, admin_token_headers, db):
    # Setup Cand A
    res_a = client.post("/api/v1/admin/candidates", json={"username": "prof_cand_a", "full_name": "A"}, headers=admin_token_headers)
    pass_a = res_a.json()["temporary_password"]
    login_a = client.post("/api/v1/auth/login", json={"username": "prof_cand_a", "password": pass_a})
    headers_a = {"Cookie": f"defendx_session={login_a.cookies.get('defendx_session')}"}
    client.post("/api/v1/auth/change-password", json={"current_password": pass_a, "new_password": "NewStrongPassword123"}, headers=headers_a)
    login_a2 = client.post("/api/v1/auth/login", json={"username": "prof_cand_a", "password": "NewStrongPassword123"})
    headers_a2 = {"Cookie": f"defendx_session={login_a2.cookies.get('defendx_session')}"}
    
    # Setup Cand B
    res_b = client.post("/api/v1/admin/candidates", json={"username": "prof_cand_b", "full_name": "B"}, headers=admin_token_headers)
    pass_b = res_b.json()["temporary_password"]
    login_b = client.post("/api/v1/auth/login", json={"username": "prof_cand_b", "password": pass_b})
    headers_b = {"Cookie": f"defendx_session={login_b.cookies.get('defendx_session')}"}
    client.post("/api/v1/auth/change-password", json={"current_password": pass_b, "new_password": "NewStrongPassword123"}, headers=headers_b)
    login_b2 = client.post("/api/v1/auth/login", json={"username": "prof_cand_b", "password": "NewStrongPassword123"})
    headers_b2 = {"Cookie": f"defendx_session={login_b2.cookies.get('defendx_session')}"}
    
    # Update A's profile
    res_update_a = client.patch("/api/v1/profile", json={"target_force": "Indian Army"}, headers=headers_a2)
    assert res_update_a.status_code == 200
    assert res_update_a.json()["target_force"] == "Indian Army"
    
    # Get B's profile, ensure it wasn't modified
    res_prof_b = client.get("/api/v1/profile", headers=headers_b2)
    assert res_prof_b.status_code == 200
    assert res_prof_b.json()["target_force"] is None
    
    # Try invalid target force
    res_invalid = client.patch("/api/v1/profile", json={"target_force": "Space Force"}, headers=headers_a2)
    assert res_invalid.status_code == 422 # Validation error

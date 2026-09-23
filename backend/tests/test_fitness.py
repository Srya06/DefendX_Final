import pytest
from datetime import datetime
from app.models.fitness import FitnessAssessment

def test_save_fitness_assessment(client, admin_token_headers):
    # We use admin_token_headers as a proxy for an authenticated session.
    # In reality it is a "CANDIDATE" doing the test, but the API just needs `current_user`.
    
    payload = {
        "id": "e412b186-b485-45a7-96a1-9bb41fbd6817",
        "exercise_type": "pushups",
        "started_at": datetime.utcnow().isoformat() + "Z",
        "completed_at": datetime.utcnow().isoformat() + "Z",
        "duration_seconds": 30.5,
        "total_reps": 15,
        "valid_reps": 12,
        "invalid_reps": 3,
        "average_confidence": 0.88,
        "form_score": 85.0,
        "form_warnings": "Keep body straight"
    }

    res = client.post("/api/v1/fitness/assessments", json=payload, headers=admin_token_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["exercise_type"] == "pushups"
    assert data["valid_reps"] == 12

def test_get_own_fitness_assessments(client, admin_token_headers):
    res = client.get("/api/v1/fitness/assessments", headers=admin_token_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1
    
    # Try fetching specific
    asm_id = res.json()[0]["id"]
    res_single = client.get(f"/api/v1/fitness/assessments/{asm_id}", headers=admin_token_headers)
    assert res_single.status_code == 200

def test_unauthorized_access(client):
    res = client.get("/api/v1/fitness/assessments")
    assert res.status_code == 401

def test_negative_reps_rejected(client, admin_token_headers):
    payload = {
        "id": "bad-id-123",
        "exercise_type": "pushups",
        "started_at": datetime.utcnow().isoformat() + "Z",
        "completed_at": datetime.utcnow().isoformat() + "Z",
        "duration_seconds": 10.0,
        "total_reps": -5,
        "valid_reps": -5,
        "invalid_reps": 0,
        "average_confidence": 0.5,
        "form_score": 100.0,
    }
    # Schema validation or explicit check should fail
    res = client.post("/api/v1/fitness/assessments", json=payload, headers=admin_token_headers)
    assert res.status_code == 422

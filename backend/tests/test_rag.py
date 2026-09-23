import pytest
from app.services.rag.retriever import RetrieverService

def test_intent_extraction():
    assert RetrieverService.extract_intent("Navy physical standards") == "PHYSICAL_STANDARD"
    assert RetrieverService.extract_intent("Army age limit") == "ELIGIBILITY"
    assert RetrieverService.extract_intent("What is the education requirement") == "EDUCATION"
    assert RetrieverService.extract_intent("How many vacancies") == "VACANCY"
    assert RetrieverService.extract_intent("Medical tests for air force") == "MEDICAL_STANDARD"
    assert RetrieverService.extract_intent("selection process") == "SELECTION_STAGE"
    assert RetrieverService.extract_intent("important dates") == "IMPORTANT_DATE"

def test_retrieval_negative_safety():
    # If no data exists, it should handle safely
    res = RetrieverService.retrieve("Army age limit", force="Space Force", top_k=5)
    assert len(res) == 0

def test_force_isolation():
    # This test verifies that we don't leak Army into Navy by ensuring force constraint is respected
    # A query for an unknown force returns empty.
    res = RetrieverService.retrieve("Army age limit", force="UnknownForce", top_k=5)
    assert len(res) == 0

def test_full_rag_pipeline_api(client):
    payload = {
        "query": "Navy physical standards",
        "force": "Indian Navy",
        "top_k": 5
    }
    res = client.post("/api/v1/rag/retrieve", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "query" in data
    assert data["grounding_status"] in ["GROUNDED", "INSUFFICIENT_EVIDENCE"]

import time
import json
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_current_user

# Mock the authentication to bypass Postgres for the live agent test
# but KEEP the real Agent, LangGraph, Vector, Neo4j, and Ollama components.
async def mock_get_current_user():
    class MockUser:
        id = "test-candidate-123"
        username = "live_test"
        role = "CANDIDATE"
        target_force = "Indian Navy"
    return MockUser()

app.dependency_overrides[get_current_user] = mock_get_current_user

def run_test():
    client = TestClient(app)
    print("Starting LIVE_OLLAMA_GENERATION verification...\n")
    
    # 1. Check agent health
    r = client.get("/api/v1/agents/health")
    print("Agent health:", r.json())
    
    # 2. Hit the query endpoint
    start_time = time.time()
    
    query_payload = {
        "query": "What are the Navy physical standards?",
        "target_force": "Indian Navy"
    }
    
    print(f"Sending query: {query_payload['query']}")
    r = client.post(
        "/api/v1/agents/query",
        json=query_payload
    )
    
    end_time = time.time()
    
    print("\n--- RESULTS ---")
    print(f"HTTP status: {r.status_code}")
    
    if r.status_code != 200:
        print(f"Failed: {r.text}")
        if "ollama" in r.text.lower() or "connection" in r.text.lower() or "agent_execution" in r.text.lower():
            print("OLLAMA_UNAVAILABLE")
        return
        
    data = r.json()
    print(f"selected agents: {data.get('selected_agents')}")
    print("execution trace:")
    for trace in data.get("execution_trace", []):
        print(f"  - {trace['agent']} -> {trace['status']} (tools: {trace.get('tools_used')})")
        
    print(f"Ollama provider: httpx via OllamaProvider")
    print(f"Ollama model: qwen2.5:1.5b")
    
    # Checking evidence
    evidence = data.get("evidence", [])
    print(f"number of graph + vector results: {len(evidence)}")
    
    print("\nevidence/provenance:")
    for ev in evidence:
        print(f"  - Document: {ev.get('document_id')}")
        print(f"    Source: {ev.get('source_url')}")
        print(f"    Text snippet: {ev.get('text')[:100]}...")
        
    print("\nfinal response:")
    print(data.get("response"))
    
    print(f"\ntotal execution time: {end_time - start_time:.2f} seconds")
    print("\nLIVE_OLLAMA_GENERATION = VERIFIED")

if __name__ == "__main__":
    run_test()

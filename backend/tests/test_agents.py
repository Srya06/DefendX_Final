import pytest
from app.services.agents.provider import OllamaProvider
from app.services.agents.graph import create_agent_graph
from app.services.agents.state import AgentState

@pytest.fixture
def mock_llm(monkeypatch):
    class MockProvider(OllamaProvider):
        async def invoke(self, prompt: str) -> str:
            if "Commander Agent" in prompt:
                return '```json\n["recruitment", "mentor", "synthesis"]\n```'
            elif "Recruitment Expert" in prompt:
                return "Mock recruitment answer"
            elif "Synthesis Agent" in prompt:
                return "Final synthesized mock answer"
            return "Generic mock answer"
    
    mock_provider = MockProvider()
    
    # We must patch the global instance used by nodes
    import app.services.agents.nodes as nodes
    monkeypatch.setattr(nodes, "llm_provider", mock_provider)
    return mock_provider

@pytest.mark.asyncio
async def test_agent_graph_execution(mock_llm):
    graph = create_agent_graph()
    initial_state: AgentState = {
        "request_id": "test-123",
        "candidate_id": "cand-123",
        "query": "What is the Navy age limit?",
        "target_force": "Indian Navy",
        "detected_intent": None,
        "selected_agents": [],
        "retrieval_evidence": [],
        "recruitment_result": None,
        "academic_result": None,
        "fitness_result": None,
        "mentor_result": None,
        "synthesis_result": None,
        "language": "en",
        "errors": [],
        "execution_trace": []
    }
    
    # Note: RAG RetrieverService is called synchronously in recruitment_node, 
    # it uses Neo4j/ChromaDB. We assume the DB is running and populated.
    final_state = await graph.ainvoke(initial_state)
    
    assert final_state["request_id"] == "test-123"
    assert "recruitment" in final_state["selected_agents"]
    assert final_state["recruitment_result"] is not None
    assert final_state["synthesis_result"] == "Final synthesized mock answer"
    
    traces = [t["agent"] for t in final_state["execution_trace"]]
    assert "commander" in traces
    assert "recruitment" in traces
    assert "synthesis" in traces

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
import uuid

from app.services.agents.state import AgentState
from app.services.agents.graph import agent_graph
from app.services.agents.provider import llm_provider

router = APIRouter()

class AgentQueryRequest(BaseModel):
    query: str
    target_force: Optional[str] = None

class AgentQueryResponse(BaseModel):
    request_id: str
    response: str
    selected_agents: List[str]
    evidence: List[Dict[str, Any]]
    execution_trace: List[Dict[str, Any]]
    warnings: List[str]

@router.post("/query", response_model=AgentQueryResponse)
async def query_agents(
    request: AgentQueryRequest,
    # In a real app we'd inject current_candidate from auth context
    # current_candidate = Depends(get_current_active_candidate)
):
    request_id = str(uuid.uuid4())
    candidate_id = "authenticated-candidate-uuid" # Hardcoded for now without real auth DB
    
    # Initialize State
    initial_state: AgentState = {
        "request_id": request_id,
        "candidate_id": candidate_id,
        "query": request.query,
        "target_force": request.target_force,
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
    
    # Execute Graph
    try:
        final_state = await agent_graph.ainvoke(initial_state)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AGENT_EXECUTION_FAILED: {str(e)}"
        )
        
    response_text = final_state.get("synthesis_result", "I am unable to provide a response at this time.")
    warnings = final_state.get("errors", [])
    
    return AgentQueryResponse(
        request_id=final_state["request_id"],
        response=response_text,
        selected_agents=final_state["selected_agents"],
        evidence=final_state["retrieval_evidence"],
        execution_trace=final_state["execution_trace"],
        warnings=warnings
    )

@router.get("/health")
async def health_check():
    return await llm_provider.health_check()

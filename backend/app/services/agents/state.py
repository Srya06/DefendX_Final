from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    request_id: str
    candidate_id: str
    query: str
    target_force: Optional[str]
    detected_intent: Optional[str]
    selected_agents: List[str]
    retrieval_evidence: List[Dict[str, Any]]
    recruitment_result: Optional[str]
    academic_result: Optional[str]
    fitness_result: Optional[str]
    mentor_result: Optional[str]
    synthesis_result: Optional[str]
    language: str
    errors: List[str]
    execution_trace: List[Dict[str, Any]]

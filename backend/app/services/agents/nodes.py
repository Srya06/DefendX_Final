from app.services.agents.state import AgentState
from app.services.agents.provider import llm_provider
from app.services.rag.retriever import RetrieverService
import json

def trace_event(state: AgentState, agent_name: str, status: str, extras: dict = None):
    event = {"agent": agent_name, "status": status}
    if extras:
        event.update(extras)
    state["execution_trace"].append(event)
    return state

async def commander_node(state: AgentState) -> AgentState:
    trace_event(state, "commander", "started")
    query = state.get("query", "")
    
    # Very simple routing logic using LLM
    prompt = f"""You are the Commander Agent for DEFEND-X recruitment platform.
Analyze this user query: "{query}"

Determine which specialist agents are needed. Reply ONLY with a JSON list containing one or more of these strings:
"recruitment", "academic", "fitness"

Always include "recruitment" for official selection, physical standards, vacancies, eligibility, and notifications.
Include "academic" for study plans or syllabus requests.
Include "fitness" for physical training or measuring metrics.

JSON List format exactly, no other text:
"""
    try:
        response = await llm_provider.invoke(prompt)
        selected_agents = json.loads(response.strip("` \n").split("```json")[-1].split("```")[0])
        if not isinstance(selected_agents, list):
            selected_agents = ["recruitment"]
    except Exception:
        # Fallback if LLM fails parsing or unavailable
        selected_agents = ["recruitment"]
        
    state["selected_agents"] = selected_agents
    trace_event(state, "commander", "completed", {"selected": selected_agents})
    return state

async def recruitment_node(state: AgentState) -> AgentState:
    trace_event(state, "recruitment", "started")
    try:
        # Hybrid Graph + Vector Retrieval
        evidence_list = RetrieverService.retrieve(
            query=state["query"],
            force=state["target_force"],
            top_k=5
        )
        
        state["retrieval_evidence"] = [e.dict() for e in evidence_list]
        
        if not evidence_list:
            state["recruitment_result"] = "INSUFFICIENT_EVIDENCE"
            trace_event(state, "recruitment", "completed", {"tools_used": ["hybrid_retrieval"], "note": "INSUFFICIENT_EVIDENCE"})
            return state

        # Construct prompt with evidence
        ev_text = "\\n".join([f"Source ({e.source_url} - Page {e.page_start}): {e.text}" for e in evidence_list])
        
        prompt = f"""You are the DEFEND-X Recruitment Expert Agent.
Answer the candidate's query using ONLY the following verified evidence. Do not use outside knowledge.
If the evidence is insufficient to fully answer, state clearly what is missing.

Query: {state['query']}
Force Context: {state['target_force'] or 'General'}

Verified Evidence:
{ev_text}

Provide a clear, evidence-grounded answer:
"""
        result = await llm_provider.invoke(prompt)
        state["recruitment_result"] = result.strip()
    except Exception as e:
        state["recruitment_result"] = f"Error in recruitment agent: {str(e)}"
        state["errors"].append(str(e))
        
    trace_event(state, "recruitment", "completed", {"tools_used": ["hybrid_retrieval"]})
    return state

async def academic_node(state: AgentState) -> AgentState:
    trace_event(state, "academic", "started")
    try:
        prompt = f"""You are the DEFEND-X Academic Agent.
Provide general study guidance for this query: "{state['query']}".
Do NOT fabricate official exam syllabus facts. Distinguish general guidance from official requirements.
"""
        result = await llm_provider.invoke(prompt)
        state["academic_result"] = result.strip()
    except Exception as e:
        state["academic_result"] = "Academic guidance currently unavailable."
        
    trace_event(state, "academic", "completed")
    return state

async def fitness_node(state: AgentState) -> AgentState:
    trace_event(state, "fitness", "started")
    # As per phase 6 requirements: no real metrics yet
    state["fitness_result"] = "FITNESS_DATA_UNAVAILABLE"
    trace_event(state, "fitness", "completed", {"note": "FITNESS_DATA_UNAVAILABLE"})
    return state

async def mentor_node(state: AgentState) -> AgentState:
    trace_event(state, "mentor", "started")
    try:
        prompt = f"""You are the DEFEND-X Mentor Agent.
Combine the candidate context and specialist outputs to provide personalized guidance.
Do NOT claim official selection or fabricate eligibility. Use cautious language around readiness.

Query: {state['query']}
Recruitment Info: {state.get('recruitment_result', 'None')}
Academic Info: {state.get('academic_result', 'None')}
Fitness Info: {state.get('fitness_result', 'None')}

Provide brief, encouraging mentor guidance:
"""
        result = await llm_provider.invoke(prompt)
        state["mentor_result"] = result.strip()
    except Exception as e:
        state["mentor_result"] = "Mentor guidance currently unavailable."
    trace_event(state, "mentor", "completed")
    return state

async def synthesis_node(state: AgentState) -> AgentState:
    trace_event(state, "synthesis", "started")
    
    try:
        prompt = f"""You are the DEFEND-X Synthesis Agent.
Your task is to reconcile results from specialist agents and generate the final authoritative response for the candidate.
Do NOT contradict authoritative verified evidence.
Clearly distinguish between VERIFIED_FACT (from recruitment), GENERAL_GUIDANCE (from mentor/academic), and UNAVAILABLE_DATA.

Query: {state['query']}
Recruitment Evidence: {state.get('recruitment_result', 'None')}
Mentor Guidance: {state.get('mentor_result', 'None')}
Academic Guidance: {state.get('academic_result', 'None')}
Fitness Status: {state.get('fitness_result', 'None')}

Generate the final, well-structured response:
"""
        result = await llm_provider.invoke(prompt)
        state["synthesis_result"] = result.strip()
    except Exception as e:
        state["synthesis_result"] = "The system could not synthesize a final response at this time."
        state["errors"].append(f"Synthesis failed: {str(e)}")
        
    trace_event(state, "synthesis", "completed")
    return state

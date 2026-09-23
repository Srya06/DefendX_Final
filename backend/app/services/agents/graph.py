from langgraph.graph import StateGraph, END
from app.services.agents.state import AgentState
from app.services.agents.nodes import (
    commander_node,
    recruitment_node,
    academic_node,
    fitness_node,
    mentor_node,
    synthesis_node
)

def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("commander", commander_node)
    workflow.add_node("recruitment", recruitment_node)
    workflow.add_node("academic", academic_node)
    workflow.add_node("fitness", fitness_node)
    workflow.add_node("mentor", mentor_node)
    workflow.add_node("synthesis", synthesis_node)
    
    # Set entry point
    workflow.set_entry_point("commander")
    
    # Define routing logic
    def route_from_commander(state: AgentState):
        agents = state.get("selected_agents", [])
        if not agents:
            return ["recruitment"]
        return agents
    
    # Commander to Specialists
    workflow.add_conditional_edges(
        "commander",
        route_from_commander,
        {
            "recruitment": "recruitment",
            "academic": "academic",
            "fitness": "fitness"
        }
    )
    
    # Specialists to Mentor
    workflow.add_edge("recruitment", "mentor")
    workflow.add_edge("academic", "mentor")
    workflow.add_edge("fitness", "mentor")
    
    # Mentor to Synthesis
    workflow.add_edge("mentor", "synthesis")
    
    # Synthesis to End
    workflow.add_edge("synthesis", END)
    
    return workflow.compile()

agent_graph = create_agent_graph()

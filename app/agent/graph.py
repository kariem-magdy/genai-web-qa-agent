from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.agent.nodes import node_explore, node_design, node_implement, node_verify

def should_refine(state: AgentState):
    """
    Conditional Logic: Loop back if failed and attempts < 3.
    """
    if state['test_results'] == "Failed" and state['attempt_count'] < 3:
        return "implement"
    return END

def build_graph():
    """
    Defines the workflow with loops for self-correction.
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("explore", node_explore)
    workflow.add_node("design", node_design)
    workflow.add_node("implement", node_implement)
    workflow.add_node("verify", node_verify)
    
    workflow.set_entry_point("explore")
    
    workflow.add_edge("explore", "design")
    workflow.add_edge("design", "implement")
    workflow.add_edge("implement", "verify")
    
    workflow.add_conditional_edges(
        "verify",
        should_refine,
        {
            "implement": "implement",
            END: END
        }
    )
    
    return workflow.compile()
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.core.state import AgentState
from app.agent.nodes import node_explore, node_design, node_implement, node_verify, node_human_approval

def should_loop(state: AgentState):
    """
    Determines if we should loop back to implementation based on Human Critique or Errors.
    This logic is handled by the Graph interrupt structure, but this conditional 
    guides the auto-retry logic before human intervention if needed.
    """
    # If auto-fail loop is needed (e.g. syntax error), we can loop here.
    # But strictly for this requirement, we flow to 'human_approval' to let the user decide.
    return "human_approval"

def build_graph():
    """
    Defines the workflow with Human-in-the-Loop interrupts.
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("explore", node_explore)
    workflow.add_node("design", node_design)
    workflow.add_node("implement", node_implement)
    workflow.add_node("verify", node_verify)
    workflow.add_node("human_approval", node_human_approval)
    
    workflow.set_entry_point("explore")
    
    workflow.add_edge("explore", "design")
    workflow.add_edge("design", "implement")
    workflow.add_edge("implement", "verify")
    workflow.add_edge("verify", "human_approval")
    
    # Loop back from approval to implement (for refinement) or END
    # This is controlled by the edge definition, but the actual decision 
    # happens when we resume from interrupt with a specific 'next' node or state update.
    workflow.add_edge("human_approval", END) 
    
    # We interrupt BEFORE 'implement' to review the Plan.
    # We interrupt BEFORE 'human_approval' to review the Verification Results.
    return workflow.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["implement", "human_approval"]
    )
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.core.state import AgentState
from app.agent.nodes import node_explore, node_design, node_implement, node_verify, node_human_approval

def check_feedback(state: AgentState):
    """
    Router: Checks if feedback exists and user approval status.
    If critique exists, loop back to Design.
    If approved or empty, End.
    """
    fb = state.get("user_feedback", "")
    approved = state.get("approved", False)
    
    # If explicitly approved, end workflow
    if approved:
        return "end"
    
    # If there's feedback/critique, go back to design to incorporate it
    if fb and len(fb.strip()) > 0 and "approve" not in fb.lower():
        return "design"
    
    return "end"

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
    
    # Conditional routing based on feedback
    workflow.add_conditional_edges(
        "human_approval",
        check_feedback,
        {
            "design": "design",  # Go back to redesign based on feedback
            "end": END            # Finish if approved
        }
    )
    
    return workflow.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["implement", "human_approval"]
    )
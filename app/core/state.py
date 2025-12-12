from typing import TypedDict, Optional, Any

class AgentState(TypedDict):
    """
    Shared memory (State) for the LangGraph workflow.
    """
    # Inputs
    url: str
    
    # Observability
    metrics: Any  # Instance of MetricsTracker
    
    # Phase 1: Exploration Data
    dom_content: str
    clean_dom: str
    screenshot_path: Optional[str]
    page_summary: str
    element_map: str
    
    # Phase 2: Design Data
    test_plan: str
    
    # Phase 3 & 4: Implementation & Verification
    generated_code: str
    execution_logs: str
    test_results: str # "Passed" or "Failed"
    
    # Refinement Loop State
    attempt_count: int
    error_feedback: str
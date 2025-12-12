import pytest
from app.core.state import AgentState

def test_state_initialization():
    state = AgentState(
        url="http://test.com", metrics=None,
        dom_content="", clean_dom="", screenshot_path=None, page_summary="",
        element_map="", test_plan="", generated_code="", execution_logs="", 
        test_results="", attempt_count=0, error_feedback=""
    )
    assert state['url'] == "http://test.com"
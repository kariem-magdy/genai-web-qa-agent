from app.core.state import AgentState
from app.core.llm import get_llm
from app.engine.browser import BrowserManager
from app.engine.dom_cleaner import DOMCleaner
from langchain_core.messages import HumanMessage
from app.core.tracing import observe # Import robust observer

# Global browser instance
browser = BrowserManager()

@observe(name="explore")
async def node_explore(state: AgentState):
    """Phase 1: Exploration."""
    url = state['url']
    await browser.navigate(url)
    
    raw_html = await browser.get_content()
    clean_dom = DOMCleaner.clean_dom(raw_html)
    screenshot = await browser.take_screenshot()
    
    llm = get_llm()
    prompt = f"""
    Analyze this DOM structure for a QA testing agent.
    1. Identify the main purpose of the page.
    2. List the interactive elements (Buttons, Inputs, Links) with their Locators.
    
    DOM Content:
    {clean_dom}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    
    state['metrics'].add_tokens(response.usage_metadata.get('total_tokens', 0))
    state['metrics'].log_step("Exploration")
    
    return {
        "dom_content": raw_html,
        "clean_dom": clean_dom,
        "screenshot_path": screenshot,
        "page_summary": response.content,
        "attempt_count": 0 
    }


@observe(name="design")
async def node_design(state: AgentState):
    """Phase 2: Collaborative Test Design."""
    llm = get_llm()
    summary = state['page_summary']
    user_feedback = state.get('user_feedback', "")
    previous_plan = state.get('test_plan', "")
    
    # Build context-aware prompt
    feedback_context = ""
    if user_feedback and len(user_feedback.strip()) > 0:
        feedback_context = f"""
    
    CRITICAL: The user provided the following feedback on the previous test plan:
    Previous Plan: {previous_plan}
    
    USER FEEDBACK/CRITIQUE:
    {user_feedback}
    
    You MUST revise the test plan to fully address this feedback. Do not ignore any of the user's requests.
    """
    
    prompt = f"""
    Based on the page analysis below, propose a Test Plan.
    Create a list of 3 distinct test scenarios (e.g., "Verify Login", "Check Header").
    
    Page Analysis:
    {summary}
    {feedback_context}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    state['metrics'].add_tokens(response.usage_metadata.get('total_tokens', 0))
    state['metrics'].log_step("Design")
    
    # Clear user_feedback after incorporating it
    return {
        "test_plan": response.content,
        "user_feedback": "",  # Clear feedback after processing
        "approved": False  # Reset approval status
    }

@observe(name="implement")
async def node_implement(state: AgentState):
    """Phase 3: Implementation."""
    llm = get_llm()
    plan = state['test_plan']
    dom = state['clean_dom']
    
    feedback = state.get('error_feedback', "")
    user_feedback = state.get('user_feedback', "")
    
    full_feedback = f"System Errors: {feedback}\nHuman Review Feedback: {user_feedback}"
    
    prompt = f"""
    You are a Senior SDET. Write a Python script using Playwright to test this page.
    
    URL: {state['url']}
    Test Plan: {plan}
    DOM Context: {dom}
    Feedback/Refinements: {full_feedback}
    
    STRICT CONSTRAINTS:
    1. Output ONLY the Python code. No markdown.
    2. Import `asyncio` and `playwright.async_api`.
    3. Use `async with async_playwright() as p:`
    4. Launch browser with `headless=False`.
    5. Wrap logic in `async def main():` and call `asyncio.run(main())`.
    6. Print "TEST PASSED" or "TEST FAILED".
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    code = response.content.replace("```python", "").replace("```", "").strip()
    
    state['metrics'].add_tokens(response.usage_metadata.get('total_tokens', 0))
    state['metrics'].log_step("Implementation")
    
    return {"generated_code": code}

@observe(name="verify")
async def node_verify(state: AgentState):
    """Phase 4: Verification."""
    code = state['generated_code']
    logs = await browser.execute_generated_test(code)
    
    result = "Failed"
    if "TEST PASSED" in logs:
        result = "Passed"
    
    state['metrics'].log_step("Verification")
    
    return {
        "execution_logs": logs,
        "test_results": result,
        "attempt_count": state['attempt_count'] + 1
    }

@observe(name="human_approval")
async def node_human_approval(state: AgentState):
    """Passive node to allow Human Critique interrupt."""
    # This node just pauses for human input
    # Return empty dict to keep state unchanged
    return {}
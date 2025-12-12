import asyncio
from app.agent.graph import build_graph
from app.core.metrics import MetricsTracker
from app.core.state import AgentState

async def run_cli():
    """
    CLI runner for End-to-End testing without UI.
    """
    print("Initializing Agent...")
    graph = build_graph()
    metrics = MetricsTracker()
    
    url = input("Enter URL to test: ")
    if not url:
        print("No URL provided. Exiting.")
        return

    # Initialize full state structure
    state = AgentState(
        url=url, 
        metrics=metrics,
        dom_content="", 
        clean_dom="", 
        screenshot_path="", 
        page_summary="",
        element_map="", 
        test_plan="", 
        generated_code="", 
        execution_logs="", 
        test_results="Pending", 
        attempt_count=0, 
        error_feedback=""
    )
    
    print("\nRunning Workflow...")
    # Using ainvoke to run the async graph
    final_state = await graph.ainvoke(state)
    
    print("\n" + "="*30)
    print("FINAL REPORT")
    print("="*30)
    print(f"URL: {final_state['url']}")
    print(f"Result: {final_state['test_results']}")
    print(f"Attempts: {final_state['attempt_count']}")
    print(f"Total Tokens: {metrics.total_tokens}")
    print("\n--- Execution Logs ---")
    print(final_state.get('execution_logs', 'No logs available.'))

if __name__ == "__main__":
    asyncio.run(run_cli())
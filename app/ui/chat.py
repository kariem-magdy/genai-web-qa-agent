import sys
import os

# Ensure root path is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import chainlit as cl
from app.agent.graph import build_graph
from app.core.metrics import MetricsTracker
from app.core.state import AgentState

app_graph = build_graph()

@cl.on_chat_start
async def start():
    cl.user_session.set("metrics", MetricsTracker())
    await cl.Message(content="**🚀 QA Testing Agent**\n\nFeatures:\n- 🌊 Streaming Tokens\n- 👁️ Visual Diffing\n\nEnter a **URL** to begin.").send()

@cl.on_message
async def main(message: cl.Message):
    url = message.content
    metrics = cl.user_session.get("metrics")
    
    # Initial State
    state = AgentState(
        url=url, 
        metrics=metrics,
        dom_content="", clean_dom="", screenshot_path="", page_summary="",
        element_map="", test_plan="", generated_code="", execution_logs="",
        test_results="Pending", attempt_count=0, error_feedback=""
    )
    
    # Active message tracker to update specific UI elements
    current_msg = None
    curr_node = None

    # Use astream_events for granular control (Streaming)
    async for event in app_graph.astream_events(state, version="v1"):
        kind = event["event"]
        name = event["name"]
        
        # 1. Handle Start of a Node (Create a new message placeholder)
        if kind == "on_chain_start" and name in ["explore", "design", "implement", "verify"]:
            curr_node = name
            if name == "explore":
                current_msg = cl.Message(content="**🔎 Exploring Page...**\n")
            elif name == "design":
                current_msg = cl.Message(content="**📝 Designing Test Plan...**\n")
            elif name == "implement":
                current_msg = cl.Message(content="**💻 Implementing Code...**\n```python\n")
            elif name == "verify":
                current_msg = cl.Message(content="**🧪 Verifying Tests...**\n")
            
            await current_msg.send()

        # 2. Handle Streaming Tokens (The "Wave")
        elif kind == "on_chat_model_stream":
            token = event["data"]["chunk"].content
            if token and current_msg:
                # Append token to the current message
                await current_msg.stream_token(token)

        # 3. Handle End of a Node (Finalize formatting)
        elif kind == "on_chain_end" and name in ["explore", "design", "implement", "verify"]:
            output = event["data"].get("output")
            if not output: continue

            if name == "explore":
                summary = output.get("page_summary", "")
                # Update with final clean content
                current_msg.content = f"**✅ Exploration Complete**\n\n{summary}"
                if output.get("screenshot_path"):
                    current_msg.elements = [cl.Image(path=output["screenshot_path"], name="initial_state", display="inline")]
                await current_msg.update()

            elif name == "design":
                plan = output.get("test_plan", "")
                current_msg.content = f"**📝 Test Plan Created**\n\n{plan}"
                await current_msg.update()

            elif name == "implement":
                code = output.get("generated_code", "")
                # Close the code block
                current_msg.content = f"**💻 Code Generated**\n```python\n{code}\n```"
                await current_msg.update()

            elif name == "verify":
                logs = output.get("execution_logs", "")
                result = output.get("test_results", "")
                
                # Check for visual diff image
                elements = []
                if os.path.exists("diff_result.png") and "[Visual Diff] Change Detected" in logs:
                    elements.append(cl.Image(path="diff_result.png", name="visual_diff", display="inline"))
                
                status_icon = "🎉" if result == "Passed" else "⚠️"
                current_msg.content = f"**{status_icon} Verification {result}**\n\nLogs:\n```\n{logs}\n```"
                current_msg.elements = elements
                await current_msg.update()
                
                # Show Metrics Footer
                stats = metrics.get_stats()
                await cl.Message(content=f"--- \n**📊 Total Metrics**: {stats['tokens']} Tokens | {stats['duration']}s").send()
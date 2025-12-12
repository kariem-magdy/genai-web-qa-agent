import sys
import os

# --- FIX: Add project root to system path ---
# This ensures Python can find the 'app' module even when running from a subfolder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# --------------------------------------------

import chainlit as cl
from app.agent.graph import build_graph
from app.core.metrics import MetricsTracker
from app.core.state import AgentState

app_graph = build_graph()

@cl.on_chat_start
async def start():
    cl.user_session.set("metrics", MetricsTracker())
    await cl.Message(content="**🚀 QA Testing Agent**\n\nI can explore a website, design tests, and run them.\nPlease enter a **URL** to begin.").send()

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
    
    msg = cl.Message(content="")
    await msg.send()
    
    async for event in app_graph.astream(state):
        for node, data in event.items():
            
            stats = metrics.get_stats()
            footer = f"\n\n--- \n**📊 Metrics**: {stats['tokens']} Tokens | {stats['duration']}s"
            
            if node == "explore":
                await cl.Message(content=f"**✅ Exploration Complete**\nSummary:\n{data.get('page_summary', '')[:500]}...").send()
                
            elif node == "design":
                await cl.Message(content=f"**📝 Test Plan Created**\n{data.get('test_plan', '')}").send()
                
            elif node == "implement":
                code = data.get('generated_code', '')
                await cl.Message(content=f"**💻 Code Generated** (Attempt {data.get('attempt_count', 0)+1})", elements=[
                    cl.Text(name="test_script.py", content=code, language="python")
                ]).send()
                
            elif node == "verify":
                logs = data.get('execution_logs', '')
                result = data.get('test_results', 'Unknown')
                
                if result == "Passed":
                    await cl.Message(content=f"**🎉 Verification Successful!**\nLogs:\n```\n{logs}\n```" + footer).send()
                else:
                    await cl.Message(content=f"**⚠️ Verification Failed**\nRefactoring code...\nLogs:\n```\n{logs}\n```").send()
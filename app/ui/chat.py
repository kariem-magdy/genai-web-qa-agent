import sys
import os
import time
import uuid

# Ensure root path is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import chainlit as cl
from app.agent.graph import build_graph
from app.core.metrics import MetricsTracker
from app.core.state import AgentState

# Initialize graph with persistence
app_graph = build_graph()

@cl.on_chat_start
async def start():
    cl.user_session.set("metrics", MetricsTracker())
    # Generate a unique thread ID for this user session's graph state
    cl.user_session.set("thread_id", str(uuid.uuid4()))
    await cl.Message(content="**🚀 QA Testing Agent**\n\nFeatures:\n- 🌊 Streaming Tokens\n- 🤝 Human-in-the-Loop Reviews\n- 📊 Real-time Metrics\n\nEnter a **URL** to begin.").send()

@cl.on_message
async def main(message: cl.Message):
    metrics = cl.user_session.get("metrics")
    thread_id = cl.user_session.get("thread_id")
    
    # Config for the graph execution
    config = {"configurable": {"thread_id": thread_id}}
    
    # 1. CHECK CURRENT GRAPH STATE
    current_state = await app_graph.aget_state(config)
    next_node = current_state.next[0] if current_state.next else None
    
    inputs = None
    resume_graph = False

    # --- SCENARIO A: NEW URL (Start Fresh) ---
    if not next_node:
        metrics.start_time = time.time()
        metrics.last_time = metrics.start_time
        metrics.total_tokens = 0
        metrics.step_times = []
        
        url = message.content
        inputs = AgentState(
            url=url, 
            metrics=metrics,
            dom_content="", clean_dom="", screenshot_path="", page_summary="",
            element_map="", test_plan="", generated_code="", execution_logs="",
            test_results="Pending", attempt_count=0, error_feedback="", user_feedback=""
        )
    
    # --- SCENARIO B: REVIEWING TEST PLAN (Paused at 'implement') ---
    elif next_node == "implement":
        user_input = message.content
        if "approve" in user_input.lower():
            await cl.Message(content="✅ **Plan Approved.** Generating code...").send()
            await app_graph.aupdate_state(config, {"user_feedback": ""})
        else:
            await cl.Message(content=f"📝 **Feedback Received.** Refining & Implementing...").send()
            await app_graph.aupdate_state(config, {"user_feedback": user_input, "test_plan": current_state.values['test_plan'] + f"\nUser Feedback: {user_input}"})
        
        inputs = None
        resume_graph = True

    # --- SCENARIO C: CRITIQUING RESULTS (Paused at 'human_approval') ---
    elif next_node == "human_approval":
        user_input = message.content
        if "approve" in user_input.lower() or "good" in user_input.lower():
             await cl.Message(content="🎉 **Workflow Complete.**").send()
             return 
        else:
            await cl.Message(content="🔄 **Critique Received.** Re-implementing...").send()
            await app_graph.aupdate_state(config, {"user_feedback": user_input, "attempt_count": 0}, as_node="human_approval")
            inputs = None
            resume_graph = True

    # 2. RUN THE GRAPH
    current_msg = None
    curr_node = None

    async for event in app_graph.astream_events(inputs, config, version="v1"):
        kind = event["event"]
        name = event["name"]
        
        # --- UI STREAMING LOGIC ---
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

        elif kind == "on_chat_model_stream" and current_msg:
            token = event["data"]["chunk"].content
            if token: await current_msg.stream_token(token)

        elif kind == "on_chain_end" and name in ["explore", "design", "implement", "verify"]:
            output = event["data"].get("output")
            if not output: continue

            if name == "explore":
                summary = output.get("page_summary", "")
                stats = metrics.get_stats()
                explore_time = next((s["step_duration"] for s in stats["steps"] if s["step"] == "Exploration"), 0.0)
                
                current_msg.content = f"**✅ Exploration Complete** (Time: {explore_time}s)\n\n{summary}"
                if output.get("screenshot_path"):
                    current_msg.elements = [cl.Image(path=output["screenshot_path"], name="initial_state", display="inline")]
                await current_msg.update()

            elif name == "design":
                plan = output.get("test_plan", "")
                current_msg.content = f"**📝 Test Plan Created**\n\n{plan}"
                current_msg.actions = [
                    cl.Action(name="approve_plan", value="approve", payload={"value": "approve"}, label="✅ Approve"),
                    cl.Action(name="reject_plan", value="reject", payload={"value": "reject"}, label="💬 Critique")
                ]
                await current_msg.update()
                await cl.Message(content="**Waiting for review:** Type 'approve' to proceed, or type your feedback.").send()

            elif name == "implement":
                code = output.get("generated_code", "")
                current_msg.content = f"**💻 Code Generated**\n```python\n{code}\n```"
                await current_msg.update()

            elif name == "verify":
                logs = output.get("execution_logs", "")
                result = output.get("test_results", "")
                status_icon = "🎉" if result == "Passed" else "⚠️"
                current_msg.content = f"**{status_icon} Verification {result}**\n\nLogs:\n```\n{logs}\n```"
                await current_msg.update()
                
                # --- DISPLAY METRICS TABLE ---
                stats = metrics.get_stats()
                metrics_table = "| Phase | Duration | Status |\n|-------|----------|--------|\n"
                for step in stats['steps']:
                    metrics_table += f"| {step['step']} | {step['step_duration']}s | Completed |\n"
                
                await cl.Message(content=f"### 📊 Execution Metrics\n\n{metrics_table}\n"
                                         f"**Total Time:** {stats['duration']}s | **Total Tokens:** {stats['tokens']}").send()
                await cl.Message(content="**Review Results:** Type 'approve' to finish, or type feedback to Re-Implement.").send()
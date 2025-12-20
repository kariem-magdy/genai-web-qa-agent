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
    cl.user_session.set("thread_id", str(uuid.uuid4()))
    cl.user_session.set("workflow_complete", False)
    cl.user_session.set("previous_urls", [])
    await cl.Message(content="**🚀 QA Testing Agent**\n\nFeatures:\n- 🌊 Streaming Tokens\n- 🤝 Human-in-the-Loop Reviews\n- 🔄 Multi-URL Testing\n\nEnter a **URL** to begin.").send()

@cl.on_message
async def main(message: cl.Message):
    metrics = cl.user_session.get("metrics")
    thread_id = cl.user_session.get("thread_id")
    workflow_complete = cl.user_session.get("workflow_complete", False)
    previous_urls = cl.user_session.get("previous_urls", [])
    
    config = {"configurable": {"thread_id": thread_id}}
    
    current_state = await app_graph.aget_state(config)
    next_node = current_state.next[0] if current_state.next else None
    
    inputs = None
    resume_graph = False

    # Helper function to detect if message is a URL
    def is_url(text: str) -> bool:
        text = text.strip()
        return text.startswith(('http://', 'https://', 'www.')) or '.' in text and ' ' not in text

    # --- SCENARIO A: NEW URL (Initial or after workflow completion) ---
    if not next_node or (workflow_complete and is_url(message.content)):
        # If workflow was complete, create new thread for new URL
        if workflow_complete:
            new_thread_id = str(uuid.uuid4())
            cl.user_session.set("thread_id", new_thread_id)
            config = {"configurable": {"thread_id": new_thread_id}}
            previous_urls.append(current_state.values.get('url', 'unknown') if current_state.values else 'unknown')
            cl.user_session.set("previous_urls", previous_urls)
            await cl.Message(content=f"📋 **Starting New Workflow** (Session #{len(previous_urls) + 1})\n").send()
        
        # Reset workflow status
        cl.user_session.set("workflow_complete", False)
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
            test_results="Pending", attempt_count=0, error_feedback="", 
            user_feedback="", approved=False
        )
    
    # --- SCENARIO B: REVIEWING TEST PLAN (Paused at 'implement') ---
    elif next_node == "implement":
        user_input = message.content
        if "approve" in user_input.lower():
            await cl.Message(content="✅ **Plan Approved.** Generating code...").send()
            # Clear feedback and mark as approved to proceed
            await app_graph.aupdate_state(config, {"user_feedback": "", "approved": False})
        else:
            # User provided critique - send back to design node
            await cl.Message(content=f"📝 **Feedback Received:** {user_input}\n\nRe-designing test plan...").send()
            # Set feedback and route back to design by pretending verify finished
            await app_graph.aupdate_state(
                config, 
                {"user_feedback": user_input, "approved": False},
                as_node="verify"  # Pretend verify node completed, which flows to human_approval
            )
        
        inputs = None
        resume_graph = True

    # --- SCENARIO C: CRITIQUING RESULTS (Paused at 'human_approval') ---
    elif next_node == "human_approval":
        user_input = message.content
        if "approve" in user_input.lower() or "good" in user_input.lower():
            await cl.Message(content="🎉 **Workflow Approved & Complete!**").send()
            # Mark as approved and let the graph end naturally
            await app_graph.aupdate_state(config, {"approved": True, "user_feedback": ""})
            # Mark workflow as complete for this session
            cl.user_session.set("workflow_complete", True)
            inputs = None
            resume_graph = True
        else:
            # User provided critique - send back to design with feedback
            await cl.Message(content=f"🔄 **Critique Received:** {user_input}\n\nRe-designing based on feedback...").send()
            await app_graph.aupdate_state(
                config, 
                {"user_feedback": user_input, "approved": False}
            )
            inputs = None
            resume_graph = True

    # 2. RUN THE GRAPH
    current_msg = None

    async for event in app_graph.astream_events(inputs, config, version="v1"):
        kind = event["event"]
        name = event["name"]
        
        if kind == "on_chain_start" and name in ["explore", "design", "implement", "verify"]:
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
                actions = [
                    cl.Action(name="approve_plan", value="approve", payload={"value": "approve"}, label="✅ Approve"),
                    cl.Action(name="reject_plan", value="reject", payload={"value": "reject"}, label="💬 Critique")
                ]
                current_msg.actions = actions
                await current_msg.update()
                await cl.Message(content="**Waiting for review:** Type 'approve' to proceed, or type your feedback/changes.").send()

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
                
                stats = metrics.get_stats()
                await cl.Message(content=f"--- \n**📊 Total Metrics**: {stats['tokens']} Tokens | {stats['duration']}s").send()
                await cl.Message(content="**Review Results:** Type 'approve' to finish, or type feedback to Re-Implement.").send()
    
    # Check if workflow just completed and prompt for new URL
    final_state = await app_graph.aget_state(config)
    if not final_state.next and cl.user_session.get("workflow_complete"):
        previous_urls = cl.user_session.get("previous_urls", [])
        session_num = len(previous_urls) + 1
        await cl.Message(content=f"\n---\n\n✨ **Ready for next test!**\n\n📝 Completed sessions: {session_num}\n\nEnter a new **URL** to test, or ask questions about previous results.").send()
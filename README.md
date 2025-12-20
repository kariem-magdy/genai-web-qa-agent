# GenAIProject — Web-based Testing Agent (Chainlit)

A Python application that uses an LLM-driven workflow to **analyze a web page**, **propose a test plan**, **generate automated test code**, and **verify execution results** through an interactive **Chainlit** chat UI.

Version: [`app.__version__`](app/__init__.py)

---

## What it does

In the Chainlit chat, you provide a target URL. The agent then runs a multi-step pipeline (streamed to the UI via [`app.ui.chat.main`](app/ui/chat.py)):

1. **Explore**: analyze the page and produce a summary  
2. **Design**: generate a test plan (see [`app.agent.nodes.node_design`](app/agent/nodes.py))  
3. **Implement**: generate executable test code  
4. **Verify**: run the code, collect logs, and iterate if needed  

---

## Key features

- **Interactive chat UI** powered by Chainlit (entry: [`app.ui.chat.main`](app/ui/chat.py))
- **LLM-backed test planning** (example: [`app.agent.nodes.node_design`](app/agent/nodes.py))
- **Automated code generation + execution loop** with logs and pass/fail reporting
- **Token/time metrics tracking** displayed in the UI (implemented in [`app.ui.chat.main`](app/ui/chat.py))
- **Automated tests** under [tests/](tests/)

---

## Project layout

High-level structure (most relevant paths):

- [app/](app/)
  - [app/ui/chat.py](app/ui/chat.py) — Chainlit message handler and streaming UX
  - [app/agent/nodes.py](app/agent/nodes.py) — agent workflow nodes (design, etc.)
- [config.py](config.py) — central configuration
- [run_agent.py](run_agent.py) — runner/entry script (project-specific)
- [generated_test_runner.py](generated_test_runner.py) — generated test execution support
- [requirements.txt](requirements.txt) — Python dependencies
- [tests/](tests/)
  - [tests/test_workflow.py](tests/test_workflow.py)
  - [tests/test_llm_connection.py](tests/test_llm_connection.py)
  - [tests/test_dom_cleaner.py](tests/test_dom_cleaner.py)
  - [tests/test_browser.py](tests/test_browser.py)
- [chainlit.md](chainlit.md) — Chainlit welcome screen content

---

## Setup

### 1) Create and activate a virtual environment

````bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
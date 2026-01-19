# GenAI Web QA Agent

A sophisticated, LLM-driven Quality Assurance (QA) agent designed to autonomously analyze web pages, design test plans, and execute automated regression tests. Built with **LangGraph**, **Chainlit**, and **Playwright**, this tool mimics the workflow of a human SDET (Software Development Engineer in Test) by iterating through exploration, planning, implementation, and verification phases with human-in-the-loop feedback.

## Project Overview

The **GenAI Web QA Agent** addresses the time-consuming nature of writing and maintaining end-to-end (E2E) web tests. Instead of manually inspecting DOM elements and writing selector-based scripts, users simply provide a URL. The agent uses Google's Gemini models to understand the page structure, propose valid test scenarios, generates the corresponding Python/Playwright code, and executes it in real-time.

It features a conversational UI that allows users to critique test plans before code generation and review results, ensuring the generated tests meet specific requirements.

## Key Features

* **Autonomous Page Analysis**: Uses a custom `DOMCleaner` to strip noise (scripts, styles, SVGs) and feed a token-optimized DOM structure to the LLM.
* **Interactive Test Design**: Proposes a 3-scenario test plan (e.g., "Verify Login", "Check Cart") which the user can approve or critique via the Chat UI.
* **Code Generation & Execution**: Automatically generates asynchronous Python Playwright code, writes it to disk (`generated_test_runner.py`), and executes it in a subprocess.
* **Human-in-the-Loop Workflow**: Built on **LangGraph**, the state machine pauses before implementation and final approval, allowing users to guide the agent.
* **Observability**: Integrated with **Langfuse** for detailed trace recording of LLM reasoning steps, token usage, and latency.
* **Live Metrics**: Tracks and displays token consumption and execution time per step in the UI.

## System Architecture

The system operates as a stateful graph defined in `app/agent/graph.py`.

### Workflow Stages

1. **Explore (`node_explore`)**: Navigates to the target URL using Playwright, captures a screenshot, cleans the DOM, and generates a page summary.
2. **Design (`node_design`)**: The LLM proposes a test plan based on the exploration data. The workflow pauses here for user approval or feedback.
3. **Implement (`node_implement`)**: Once the plan is approved, the LLM generates a complete Python script using `async_playwright`.
4. **Verify (`node_verify`)**: The system executes the generated code. It captures standard output, errors, and pass/fail status.
5. **Human Approval (`node_human_approval`)**: The user reviews the execution logs. If the tests failed or were insufficient, the user provides feedback, and the agent loops back to the **Design** phase to refine the plan.

## Tech Stack

* **Language**: Python 3.9+
* **Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/) (State machine management)
* **LLM Integration**: [LangChain](https://www.langchain.com/) (Google GenAI integration)
* **Model**: Google Gemini (Configured as `gemini-2.5-flash-lite`)
* **Browser Automation**: [Playwright](https://playwright.dev/) (Async API)
* **User Interface**: [Chainlit](https://docs.chainlit.io/) (Chat interface & streaming)
* **Observability**: [Langfuse](https://langfuse.com/) (Tracing & Evaluation)
* **Testing**: Pytest (Unit & Integration tests)

## Repository Structure

```text
GenAIProject/
├── app/
│   ├── agent/              # Core Agent Logic
│   │   ├── graph.py        # LangGraph workflow definition
│   │   └── nodes.py        # Implementation of Explore, Design, Implement, Verify nodes
│   ├── core/               # System Utilities
│   │   ├── llm.py          # Gemini model configuration
│   │   ├── state.py        # AgentState TypedDict definition
│   │   ├── tracing.py      # Langfuse integration
│   │   └── metrics.py      # Token and time tracking
│   ├── engine/             # Browser & DOM Handling
│   │   ├── browser.py      # Playwright manager (startup, nav, screenshot)
│   │   └── dom_cleaner.py  # BeautifulSoup logic to optimize HTML for LLM
│   └── ui/
│       └── chat.py         # Chainlit entry point and message handlers
├── tests/                  # Unit and Integration Tests
├── config.py               # Environment & Model configuration
├── chainlit.md             # Welcome screen markdown
├── requirements.txt        # Project dependencies
├── run_agent.py            # CLI entry point (headless mode)
└── generated_test_runner.py # Dynamically generated test code (overwritten per run)
```

## Installation & Setup

### Prerequisites

* Python 3.10 or higher
* Google AI Studio API Key
* (Optional) Langfuse Public/Secret Keys for tracing

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/GenAIProject.git
cd GenAIProject
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 4: Configure Environment

Create a `.env` file in the root directory:

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (for Tracing)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

## Usage

### Option A: Interactive Web UI (Recommended)

Launch the Chainlit interface to interact with the agent visually.

```bash
chainlit run app/ui/chat.py -w
```

* The UI will open at `http://localhost:8000`.
* Enter a URL (e.g., `https://automationexercise.com`) to begin testing.

### Option B: CLI Mode

Run the agent directly from the terminal without the web UI.

```bash
python run_agent.py
```

* Follow the prompt to enter the URL to test.

## Configuration

The `config.py` file controls global settings:

| Parameter | Default | Description |
| --- | --- | --- |
| `MODEL_NAME` | `gemini-2.5-flash-lite` | The specific Gemini model version used. |
| `HEADLESS` | `False` | Whether to show the browser UI during tests. |
| `TIMEOUT` | `60000` | Navigation and execution timeout in milliseconds. |

## Testing

The project includes its own unit tests to ensure the agent's components work correctly.

```bash
# Run all tests
pytest tests/

# Run specific tests for the browser engine
pytest tests/test_browser.py
```

## Limitations & Assumptions

* **Stateless Tests**: The generated tests currently run as isolated scripts. They do not persist cookies or session state between the "Explore" phase and the "Verify" phase unless explicitly coded by the LLM.
* **Complex Interactions**: While capable of handling standard forms and navigation, the agent may struggle with complex, multi-frame applications or CAPTCHAs.
* **Token Limits**: `DOMCleaner` truncates HTML content to ~8000 tokens to fit within context windows. Extremely large pages may have footer content cut off.

## License

This project is licensed under the **MIT License**.

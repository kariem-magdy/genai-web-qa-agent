import time
import functools
from contextvars import ContextVar
from langfuse import Langfuse
from config import Config

# Initialize Langfuse Client
langfuse_client = None
if Config.LANGFUSE_PUBLIC_KEY and Config.LANGFUSE_SECRET_KEY:
    langfuse_client = Langfuse(
        public_key=Config.LANGFUSE_PUBLIC_KEY,
        secret_key=Config.LANGFUSE_SECRET_KEY,
        host=Config.LANGFUSE_HOST
    )

# Context variable to store the Langchain handler for the current phase span
_current_callback: ContextVar = ContextVar("current_callback", default=None)

def get_current_callback():
    """Returns the callback handler for the active span context."""
    return _current_callback.get()

def observe_phase(phase_name: str):
    """
    Decorator to wrap agent nodes. 
    Captures timing and links LLM generations to specific phases.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(state, *args, **kwargs):
            if not langfuse_client:
                return await func(state, *args, **kwargs)

            # Use state object ID as a stable trace ID for the entire workflow run
            trace_id = f"run_{id(state)}"
            trace = langfuse_client.trace(name="WebTestingAgent", id=trace_id)
            
            # Create a span for the specific phase
            span = trace.span(name=phase_name, start_time=time.time())
            
            # Set the Langchain callback to link LLM calls to this span
            handler = span.langchain_handler()
            token = _current_callback.set(handler)
            
            start_time = time.time()
            try:
                result = await func(state, *args, **kwargs)
                duration = time.time() - start_time
                
                # 3️⃣ Performance Evaluation (Explore Phase)
                if phase_name == "Exploration":
                    print(f"\n[OBSERVABILITY] Explore Phase Speed: {duration:.2f}s")
                
                span.end(metadata={"duration": duration})
                return result
            except Exception as e:
                span.end(level="ERROR", status_message=str(e))
                raise e
            finally:
                _current_callback.reset(token)
                
        return wrapper
    return decorator
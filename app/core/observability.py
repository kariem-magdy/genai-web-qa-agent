import time
import functools
from config import Config

# This import works in Langfuse v2.0.0+ (including your v3.11.1)
try:
    from langfuse.decorators import observe, langfuse_context
    from langfuse import Langfuse
except ImportError as e:
    # If this triggers, it means a local file named 'langfuse.py' is likely blocking the library
    raise ImportError(f"Could not import langfuse.decorators. Check for local 'langfuse.py' files. Error: {e}")

# Initialize Langfuse Client (for custom ops if needed)
langfuse_client = None
if Config.LANGFUSE_PUBLIC_KEY and Config.LANGFUSE_SECRET_KEY:
    langfuse_client = Langfuse(
        public_key=Config.LANGFUSE_PUBLIC_KEY,
        secret_key=Config.LANGFUSE_SECRET_KEY,
        host=Config.LANGFUSE_HOST
    )

def observe_phase(phase_name: str):
    """
    Decorator to wrap agent nodes. 
    Captures timing and links LLM generations to specific phases.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(state, *args, **kwargs):
            # 1. Generate a stable Trace ID
            seed = state.get('url', str(id(state)))
            trace_id = Langfuse.create_trace_id(seed=f"run_{seed}")
            
            # 2. Use the @observe decorator
            @observe(name=phase_name, langfuse_trace_id=trace_id)
            async def instrumented_node():
                start_time = time.time()
                try:
                    result = await func(state, *args, **kwargs)
                    duration = time.time() - start_time
                    
                    # 3. Log Performance (Explore Phase)
                    if phase_name == "Exploration":
                        print(f"\n[OBSERVABILITY] Explore Phase Speed: {duration:.2f}s")
                    
                    # Log step to internal state metrics
                    if 'metrics' in state and hasattr(state['metrics'], 'log_step'):
                        state['metrics'].log_step(phase_name)
                    
                    return result
                except Exception as e:
                    if langfuse_context:
                        langfuse_context.update_current_observation(
                            level="ERROR", 
                            status_message=str(e)
                        )
                    raise e
            
            return await instrumented_node()
                
        return wrapper
    return decorator

def get_current_callback():
    """Link Langchain LLM calls to the current trace."""
    try:
        return langfuse_context.get_current_langchain_handler()
    except Exception:
        return None
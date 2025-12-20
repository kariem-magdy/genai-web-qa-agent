import os
from functools import wraps
from inspect import iscoroutinefunction
from loguru import logger


# --- Robust Langfuse Setup ---
class DummyLangfuse:
    """Fallback class if Langfuse is not configured."""
    def trace(self, *args, **kwargs): return self
    def span(self, *args, **kwargs): return self
    def event(self, *args, **kwargs): return self
    def score(self, *args, **kwargs): return self
    def generation(self, *args, **kwargs): return self
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def update(self, *args, **kwargs): pass
    def end(self, *args, **kwargs): pass
    def flush(self): pass


class DummyCallbackHandler:
    """Fallback CallbackHandler if Langfuse is not configured."""
    pass


# Dummy decorator for @observe
def dummy_observe(*args, **kwargs):
    def decorator(func):
        if iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*f_args, **f_kwargs):
                return await func(*f_args, **f_kwargs)
            return async_wrapper
        @wraps(func)
        def wrapper(*f_args, **f_kwargs):
            return func(*f_args, **f_kwargs)
        return wrapper
    return decorator


langfuse = None
observe = None
CallbackHandler = None

try:
    # Try importing Langfuse components
    from langfuse import Langfuse
    from langfuse.callback import CallbackHandler as LangfuseCallbackHandler
    
    # Try to import observe decorator (may not exist in all versions)
    try:
        from langfuse.decorators import observe as real_observe
    except ImportError:
        try:
            from langfuse import observe as real_observe
        except ImportError:
            real_observe = None
    
    # Check for keys
    if os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY"):
        langfuse = Langfuse()
        observe = real_observe if real_observe else dummy_observe
        CallbackHandler = LangfuseCallbackHandler
        logger.info("Langfuse tracing enabled.")
    else:
        raise ValueError("Langfuse keys missing in environment.")

except Exception as e:
    logger.warning(f"Tracing disabled (Reason: {e}). Using dummy tracer.")
    langfuse = DummyLangfuse()
    observe = dummy_observe
    CallbackHandler = DummyCallbackHandler


def get_langfuse_callback():
    """
    Returns the LangChain CallbackHandler if tracing is enabled, else None.
    This bridges the gap between the SDK (observe) and LangChain's internal tracing.
    """
    try:
        if CallbackHandler and CallbackHandler is not DummyCallbackHandler:
            return CallbackHandler()
    except Exception:
        pass
    return None
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config
from app.core.observability import get_current_callback

def get_llm():
    """
    Returns the configured Gemini model with observability callbacks.
    """
    if not Config.GOOGLE_API_KEY:
        raise ValueError("Google API Key is missing. Check .env file.")
        
    config = Config.LLM
    
    return ChatGoogleGenerativeAI(
        model=config.model_name,
        google_api_key=Config.GOOGLE_API_KEY,
        temperature=config.temperature,
        top_p=config.top_p,
        max_output_tokens=config.max_tokens,
        convert_system_message_to_human=True,
        callbacks=[get_current_callback()] if get_current_callback() else []
    )
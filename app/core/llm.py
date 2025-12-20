from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config

def get_llm():
    """
    Returns the configured Gemini Free Tier model.
    """
    if not Config.GOOGLE_API_KEY:
        raise ValueError("Google API Key is missing. Check .env file.")
        
    return ChatGoogleGenerativeAI(
        model=Config.MODEL_NAME,
        google_api_key=Config.GOOGLE_API_KEY,
        temperature=0.1, # Low temperature for more deterministic code generation
        convert_system_message_to_human=True
    )
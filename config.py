import os
from dotenv import load_dotenv
from enum import Enum
from pydantic import BaseModel
from typing import Optional

load_dotenv()

# --- MANDATORY LLM CONFIGURATION ---
class LLMProvider(str, Enum):
   GROQ = "groq"
   GEMINI = "gemini"
   OPENAI = "openai"


class LLMConfig(BaseModel):
   provider: LLMProvider = LLMProvider.GEMINI
   base_url: Optional[str] = None
   model_name: str = "gemini-2.0-flash-lite"
   temperature: float = 0.7
   top_p: float = 0.7
   max_tokens: Optional[int] = 4096
   reasoning_effort: Optional[str] = "medium"

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Langfuse Keys
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    # Bridging existing code to new LLMConfig
    LLM = LLMConfig()
    MODEL_NAME = LLM.model_name 
    HEADLESS = False
    TIMEOUT = 60000

if not Config.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")
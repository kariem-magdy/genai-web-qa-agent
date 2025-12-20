import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    # FIX: Update model name to a fully qualified version tag
    MODEL_NAME = "gemini-2.5-flash-lite" 
    HEADLESS = False  # Set to False to see the browser as required
    TIMEOUT = 60000

if not Config.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")
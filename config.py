import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = "gemini-1.5-flash"
    HEADLESS = False  # Set to False to see the browser as required [cite: 8]
    TIMEOUT = 30000

if not Config.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")
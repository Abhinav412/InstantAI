import os

# -------- Groq (REQUIRED) --------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set")


# -------- Google (OPTIONAL) --------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_CSE_ID")

GOOGLE_ENABLED = bool(GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID)

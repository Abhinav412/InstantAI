import os
from groq import Groq

_client = None

def get_llm():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

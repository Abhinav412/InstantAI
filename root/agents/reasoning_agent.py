import os
from groq import Groq
from agents.config import GROQ_API_KEY, GROQ_MODEL

_client = os.getenv("GROQ_API_KEY")


def reason(prompt: str, system_context: str) -> str:
    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_context},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1024,
    )

    return response.choices[0].message.content.strip()

import os, json, re
from groq import Groq, APIConnectionError
import time

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"

def extract_json(text: str):
    if not text:
        raise ValueError("Empty LLM response")

    # Fast path: exact JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Robust path: find first valid JSON object
    stack = []
    start = None

    for i, ch in enumerate(text):
        if ch == "{":
            if not stack:
                start = i
            stack.append(ch)
        elif ch == "}":
            if stack:
                stack.pop()
                if not stack and start is not None:
                    candidate = text[start : i + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break

    raise ValueError(f"Invalid JSON from LLM:\n{text}")

def call_llm(system, user, retries=3, temperature=0.1):
    last_error = None

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=temperature
            )

            content = response.choices[0].message.content.strip()
            return extract_json(content)

        except APIConnectionError as e:
            last_error = e
            print(f"⚠️ Groq connection failed (attempt {attempt+1}/{retries})")
            time.sleep(1.5)

    raise RuntimeError("Groq API failed after retries") from last_error


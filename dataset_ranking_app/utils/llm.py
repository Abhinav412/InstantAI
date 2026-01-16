import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_json(text: str) -> dict:
    """
    Extracts the first complete JSON object using brace balance.
    Handles nested objects correctly.
    """

    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in LLM response")

    brace_count = 0
    end = None

    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1

        if brace_count == 0:
            end = i + 1
            break

    if end is None:
        raise ValueError("Unbalanced JSON braces in LLM response")

    raw = text[start:end]

    # Normalize quotes (Groq/LLaMA sometimes uses single quotes)
    raw = raw.replace("'", '"')

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid JSON from LLM:\n{raw}"
        ) from e


def call_llm(system: str, user: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    return extract_json(content)

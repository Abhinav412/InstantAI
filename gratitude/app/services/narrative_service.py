import json
from app.core.llm import get_llm
from app.models.narrative import Narrative
from app.db.session import get_session

SYSTEM_PROMPT = """
You are an information extraction system.
Extract structured attributes from gratitude messages.
Return ONLY valid JSON. No explanations.
"""

USER_PROMPT_TEMPLATE = """
Extract the following fields from the message.

Required JSON schema:
{{
  "entity_type": "person | place | team | unknown",
  "role": null,
  "actions": [],
  "descriptors": [],
  "time_context": null,
  "location_context": null,
  "sentiment_score": 0.0
}}

Message:
\"\"\"{text}\"\"\"
"""


async def parse_narrative(message_id: str, text: str):
    # 1️⃣ Call LLM (NO DB SESSION OPEN)
    client = get_llm()

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(text=text)},
        ],
        temperature=0,
    )

    raw = response.choices[0].message.content

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"LLM returned invalid JSON: {raw}")

    # 2️⃣ Persist Narrative (SHORT-LIVED SESSION)
    with get_session() as session:
        narrative = Narrative(
            message_id=message_id,
            entity_type=data.get("entity_type"),
            role=data.get("role"),
            actions=data.get("actions", []),
            descriptors=data.get("descriptors", []),
            time_context=data.get("time_context"),
            location_context=data.get("location_context"),
            sentiment_score=data.get("sentiment_score", 0.0),
        )

        session.add(narrative)
        session.flush()

        narrative_id = narrative.id

    return {"narrative_id": str(narrative_id)}

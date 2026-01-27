from app.models.message import Message
from app.db.session import get_session
from app.services.narrative_service import parse_narrative
from app.services.embedding_service import embed_narrative
from app.models.narrative import Narrative

async def ingest_message(payload: dict):
    # 1️⃣ Create and persist Message
    with get_session() as session:
        message = Message(
            raw_text=payload["text"],
            source=payload.get("source", "unknown"),
            language=payload.get("language", "en"),
            extra_metadata=payload.get("metadata", {})
        )

        session.add(message)
        session.flush()   # ensures message.id is available

        message_id = message.id
        message_text = message.raw_text

    # 2️⃣ Parse narrative (LLM / async work — NO DB SESSION OPEN)
    narrative_result = await parse_narrative(
        message_id=message_id,
        text=message_text
    )

    narrative_id = narrative_result["narrative_id"]

    # 3️⃣ Load narrative + embed (fresh session)
    with get_session() as session:
       embed_narrative(narrative_result["narrative_id"])


    return {
        "message_id": str(message_id),
        "narrative_id": str(narrative_id)
    }

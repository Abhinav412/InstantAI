"""MongoDB Logger node — persists verified documents to MongoDB.

Uses motor (async pymongo) to upsert documents into the `raw_documents`
collection.  Maintains a session document for tracking and prevents
duplicates via URL-keyed upsert.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from motor.motor_asyncio import AsyncIOMotorClient

from crawler.config import Configuration
from crawler.state import State

_client: AsyncIOMotorClient | None = None


def _get_client() -> AsyncIOMotorClient:
    """Lazy-initialise the motor client."""
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        _client = AsyncIOMotorClient(uri)
    return _client


async def log_to_mongo(
    state: State, config: Optional[RunnableConfig] = None
) -> dict[str, Any]:
    """Upsert verified documents into MongoDB and track the session."""
    configuration = Configuration.from_runnable_config(config)

    client = _get_client()
    db = client[configuration.mongo_db_name]
    raw_col = db["raw_documents"]
    session_col = db["sessions"]

    now = datetime.now(timezone.utc)

    # ── Create / update session ────────────────────────────
    session_id = state.session_id
    if not session_id:
        result = await session_col.insert_one(
            {
                "user_query": state.user_query,
                "status": "crawling",
                "created_at": now,
                "updated_at": now,
                "retry_count": state.retry_count,
            }
        )
        session_id = str(result.inserted_id)
    else:
        from bson import ObjectId

        await session_col.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"status": "crawling", "updated_at": now}},
        )

    # ── Upsert documents ───────────────────────────────────
    doc_ids: list[str] = []
    for src in state.verified_sources:
        result = await raw_col.update_one(
            {"url": src.url},
            {
                "$set": {
                    "url": src.url,
                    "content": src.content,
                    "credibility_score": src.credibility_score,
                    "relevance_score": src.relevance_score,
                    "is_trusted": src.is_trusted,
                    "session_id": session_id,
                    "updated_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )
        doc_id = str(result.upserted_id or "existing")
        doc_ids.append(doc_id)

    print(
        f"[MongoDB Logger] Upserted {len(doc_ids)} docs to '{configuration.mongo_db_name}.raw_documents'"
    )

    return {"raw_doc_ids": doc_ids, "session_id": session_id}

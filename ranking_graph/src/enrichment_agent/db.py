"""Database module for MongoDB storage."""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pymongo import MongoClient
from bson.objectid import ObjectId


MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["ranking_app"]


def save_research_session(user_id: str, topic: str, preferences: Dict[str, Any]) -> str:
    """Creates a research session and returns session_id."""
    doc = {
        "user_id": user_id,
        "topic": topic,
        "preferences": preferences,
        "status": "planning",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = db.research_sessions.insert_one(doc)
    return str(result.inserted_id)


def update_session_status(session_id: str, status: str):
    """Updates the status of a research session."""
    db.research_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}},
    )


def save_crawled_data(
    session_id: str, url: str, content: str, metadata: Dict[str, Any]
):
    """Stores crawled data linked to the session."""
    doc = {
        "session_id": ObjectId(session_id),
        "url": url,
        "content": content,
        "metadata": metadata,
        "crawled_at": datetime.utcnow(),
    }
    db.crawled_data.insert_one(doc)

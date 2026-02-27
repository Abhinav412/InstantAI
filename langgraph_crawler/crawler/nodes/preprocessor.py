"""Preprocessor node — extracts structured entities with metrics from verified documents.

Performs text cleaning and LLM-driven entity extraction. Instructs the LLM to identify
the underlying entities related to the user's query and their public metrics (funding, location, etc.).
Writes results to the `extracted_entities` MongoDB collection.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Optional

import replicate
from langchain_core.runnables import RunnableConfig
from motor.motor_asyncio import AsyncIOMotorClient

from crawler.config import Configuration
from crawler.cost_tracker import tracker
from crawler.models import ExtractedEntity
from crawler.state import State

_client: AsyncIOMotorClient | None = None


def _get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        _client = AsyncIOMotorClient(uri)
    return _client


# ── Text cleaning ────────────────────────────────────────────
def _clean_text(text: str) -> str:
    """Strip leftover HTML artifacts and normalise whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)  # strip HTML tags
    text = re.sub(r"&[a-zA-Z]+;", " ", text)  # HTML entities
    text = re.sub(r"\s+", " ", text).strip()  # collapse whitespace
    return text


_EXTRACT_PROMPT = """\
You are an expert data extraction analyst building a comparison engine.
Given the user's search query and the text of a webpage, extract all specific ENTITIES 
that match the intent of the search (e.g., if the user searches for "startup incubators in India", 
extract each incubator mentioned).

For each entity, extract relevant public METRICS as a flat dictionary of strings.
Example metrics: "Location", "Funding Amount", "Equity Taken", "Industries", "Notable Startups".

Return a JSON array of objects. Each object MUST have exactly these keys:
- "name": String (Entity name)
- "description": String (1-2 sentence description)
- "metrics": Object (Key-value pairs of extracted metrics/data points. Keys should be Title Case.)
- "priority_score": Float 0.0-1.0 (How well this entity matches the user's core intent)

User query: {query}

Document Content (truncated to 4000 chars):
{content}

Return ONLY the JSON array, no markdown brackets ```json, no explanation. If no relevant entities are found, return an empty array [].
"""


async def preprocess(
    state: State, config: Optional[RunnableConfig] = None
) -> dict[str, Any]:
    """Extract structured entities from verified documents."""
    configuration = Configuration.from_runnable_config(config)

    extracted: list[ExtractedEntity] = []
    entity_aggregator: dict[str, ExtractedEntity] = {}

    for src in state.verified_sources:
        clean_content = _clean_text(src.content)

        prompt = _EXTRACT_PROMPT.format(
            query=state.user_query,
            content=clean_content[:4000],
        )

        t0 = time.time()
        try:
            output = replicate.run(
                configuration.model,
                input={
                    "prompt": prompt,
                    "max_tokens": 1024,
                    "temperature": 0.1,
                },
            )
            raw_text = "".join(str(chunk) for chunk in output)
            latency = time.time() - t0

            input_tokens = len(prompt) // 4
            output_tokens = len(raw_text) // 4
            tracker.record(
                node="preprocessor",
                model=configuration.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_s=latency,
            )

            # Parse expected JSON array
            cleaned_resp = raw_text.strip()
            if cleaned_resp.startswith("```"):
                cleaned_resp = cleaned_resp.split("\n", 1)[1]
                cleaned_resp = cleaned_resp.rsplit("```", 1)[0]

            entities_data = json.loads(cleaned_resp)
            if not isinstance(entities_data, list):
                if isinstance(entities_data, dict) and "name" in entities_data:
                    entities_data = [entities_data]
                else:
                    entities_data = []

            for data in entities_data:
                name = data.get("name", "Unknown Entity")
                norm_name = name.lower().strip()
                if not norm_name:
                    continue

                desc = data.get("description", "")
                metrics = data.get("metrics", {})
                priority = float(data.get("priority_score", 0.5))

                if norm_name in entity_aggregator:
                    existing = entity_aggregator[norm_name]
                    # Keep the higher priority
                    if priority > existing.priority_score:
                        existing.priority_score = priority

                    # Keep the longest description
                    if len(desc) > len(existing.description):
                        existing.description = desc

                    # Merge strings for source URL just to keep track
                    if src.url not in existing.source_url:
                        existing.source_url += f", {src.url}"

                    # Merge metrics
                    for k, v in metrics.items():
                        if k in existing.metrics:
                            # If overlapping, just keep the longest/most descriptive, or concat
                            if str(v) not in str(existing.metrics[k]):
                                existing.metrics[k] = f"{existing.metrics[k]} | {v}"
                        else:
                            existing.metrics[k] = v
                else:
                    entity_aggregator[norm_name] = ExtractedEntity(
                        name=name,
                        description=desc,
                        metrics=metrics,
                        source_url=src.url,
                        priority_score=priority,
                        original_content=clean_content,
                    )
        except Exception as exc:
            print(f"[Preprocessor] Failed extraction for {src.url}: {exc}")

    # Transfer aggregated entities to the final list
    extracted = list(entity_aggregator.values())

    # ── Write to MongoDB extracted_entities collection ───
    try:
        if extracted:
            client = _get_client()
            db = client[configuration.mongo_db_name]
            proc_col = db["extracted_entities"]
            now = datetime.now(timezone.utc)

            operations = []
            for entity in extracted:
                operations.append(
                    {
                        "name": entity.name,
                        **entity.model_dump(),
                        "session_id": state.session_id,
                        "updated_at": now,
                        "created_at": now,  # Keep simple for PoC
                    }
                )
            if operations:
                await proc_col.insert_many(operations)
    except Exception as exc:
        print(f"[Preprocessor] MongoDB write failed: {exc}")

    # ── Attach cost summary to state ─────────────────────
    cost_summary = tracker.get_summary()

    print(f"[Preprocessor] Extracted {len(extracted)} distinct entities")
    tracker.print_report()

    return {"extracted_entities": extracted, "cost_summary": cost_summary}

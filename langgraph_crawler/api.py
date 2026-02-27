"""FastAPI server for the LangGraph Crawler Pipeline.

Provides REST endpoints for:
  POST /crawl          — Run the full pipeline
  GET  /crawl/{id}     — Get results for a session
  GET  /health         — Health check
  GET  /cost-summary   — Latest cost report

Run:
    uv run uvicorn api:app --reload --port 8000
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

from crawler.graph import graph  # noqa: E402
from crawler.cost_tracker import tracker  # noqa: E402

# ── App ──────────────────────────────────────────────────────
app = FastAPI(
    title="LangGraph Crawler Pipeline",
    description=(
        "A 6-node web research pipeline: Intent Parser → URL Discovery → "
        "Web Crawler → Source Verifier → MongoDB Logger → Preprocessor"
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory job store ──────────────────────────────────────
_jobs: dict[str, dict[str, Any]] = {}


# ── Request / Response models ────────────────────────────────
class CrawlRequest(BaseModel):
    """Request body for the /crawl endpoint."""

    query: str = Field(
        ...,
        description="The research query to process.",
        examples=["Latest advancements in AI agents 2025"],
    )
    max_retries: int = Field(
        default=2,
        ge=0,
        le=5,
        description="Max retry loops if too few results.",
    )
    min_credibility: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum credibility score to keep a source.",
    )


class CrawlResponse(BaseModel):
    """Response from the /crawl endpoint."""

    job_id: str
    status: str
    message: str


class ExtractedEntityResponse(BaseModel):
    name: str
    description: str
    metrics: dict[str, str]
    source_url: str
    priority_score: float


class JobResult(BaseModel):
    job_id: str
    status: str
    query: str
    started_at: str
    completed_at: str | None = None
    entities: list[ExtractedEntityResponse] = []
    cost_summary: dict[str, Any] = {}
    error: str | None = None


# ── Background pipeline runner ───────────────────────────────
async def _run_pipeline(job_id: str, query: str, config: dict) -> None:
    """Execute the graph in the background and store results."""
    try:
        result = await graph.ainvoke(
            {"user_query": query},
            config={"configurable": config},
        )

        entities = result.get("extracted_entities", [])
        _jobs[job_id]["status"] = "completed"
        _jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        _jobs[job_id]["entities"] = [
            {
                "name": e.name,
                "description": e.description,
                "metrics": e.metrics,
                "source_url": e.source_url,
                "priority_score": e.priority_score,
            }
            for e in entities
        ]
        _jobs[job_id]["cost_summary"] = result.get("cost_summary", {})
    except Exception as exc:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(exc)
        _jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()


# ── Endpoints ────────────────────────────────────────────────
@app.post("/crawl", response_model=CrawlResponse, status_code=202)
async def start_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
):
    """Start a new crawl pipeline run.

    Returns a job ID immediately. Poll GET /crawl/{job_id} for results.
    """
    job_id = str(uuid.uuid4())[:8]

    _jobs[job_id] = {
        "job_id": job_id,
        "status": "running",
        "query": request.query,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "entities": [],
        "cost_summary": {},
        "error": None,
    }

    config = {
        "max_retries": request.max_retries,
        "min_credibility": request.min_credibility,
    }

    background_tasks.add_task(_run_pipeline, job_id, request.query, config)

    return CrawlResponse(
        job_id=job_id,
        status="running",
        message=f"Pipeline started. Poll GET /crawl/{job_id} for results.",
    )


@app.get("/crawl/{job_id}", response_model=JobResult)
async def get_crawl_result(job_id: str):
    """Get the result of a crawl pipeline run."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return JobResult(**_jobs[job_id])


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "graph_name": graph.name,
        "active_jobs": sum(1 for j in _jobs.values() if j["status"] == "running"),
    }


@app.get("/cost-summary")
async def cost_summary():
    """Return the cumulative cost tracker summary across all runs."""
    return tracker.get_summary()

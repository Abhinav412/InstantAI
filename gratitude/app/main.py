from fastapi import FastAPI
from app.api.ingest import router as ingest_router
from app.api.entities import router as entity_router
from app.api.entity_resolution import router as entity_resolution_router
from app.api.review import router as review_router
from app.api.search import router as search_router
from app.api.analytics import router as analytics_router

app = FastAPI(title="Gratitude")

app.include_router(ingest_router, prefix="/api")
app.include_router(entity_router, prefix="/api/entities")
app.include_router(entity_resolution_router, prefix="/api/entity-resolution")
app.include_router(review_router, prefix="/api/review")
app.include_router(search_router, prefix="/api/search")
app.include_router(analytics_router, prefix="/api/analytics")

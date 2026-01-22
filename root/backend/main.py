from fastapi import FastAPI
from backend.api.upload import router as upload_router
from backend.api.analyze import router as analyze_router
from backend.api.rank import router as rank_router
from backend.api.chat import router as chat_router

app = FastAPI(title="Agentic Analytics Engine")

app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(rank_router)
app.include_router(chat_router)

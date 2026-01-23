from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.upload import router as upload_router
from backend.api.analyze import router as analyze_router
from backend.api.rank import router as rank_router
from backend.api.chat import router as chat_router
from backend.api.load import router as load_router

app = FastAPI(title="Agentic Analytics Engine")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(rank_router)
app.include_router(chat_router)
app.include_router(load_router)

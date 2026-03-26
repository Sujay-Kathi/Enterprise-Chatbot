"""Main FastAPI Entry Point."""

from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn

from app.api import auth_routes, chat_routes, document_routes
from app.core.config import get_settings

# --- Initialize App ---
app = FastAPI(
    title="Enterprise RAG Chatbot",
    description="A production-ready AI Assistant powered by NVIDIA NIM (Llama 3.1 8B).",
    version="1.0.0",
)

settings = get_settings()

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
app.include_router(auth_routes.router)
app.include_router(document_routes.router)
app.include_router(chat_routes.router)

# --- Health Check ---
@app.get("/", tags=["Health"], status_code=status.HTTP_200_OK)
async def health_check():
    """Verify that the API server is up and running."""
    return {
        "status": "online",
        "service": "Enterprise RAG Chatbot API",
        "api_v1": "active"
    }

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    """Ensure data directories exist on startup."""
    import os
    os.makedirs(settings.faiss_index_path, exist_ok=True)
    logger.info("🎬 FastAPI server starting up...")
    logger.info(f"📍 FAISS index located at: {settings.faiss_index_path}")

# --- Local Development ---
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

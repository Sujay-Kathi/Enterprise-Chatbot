"""Chat and Retrieval routes: Process user questions with RAG context."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from loguru import logger

from app.core import dependencies
from app.services import rag_service, moderation_service

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

class ChatMessage(BaseModel):
    role: str # 'user' or 'assistant'
    content: str

class ChatQuery(BaseModel):
    query: str = Field(..., min_length=2, max_length=1500)
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    answer: str
    emotion: str
    sources: List[str]

@router.post("/query", response_model=ChatResponse)
async def chat_query(
    payload: ChatQuery,
    current_user: str = Depends(dependencies.get_current_user)
):
    """
    RAG Pipeline:
    1. Moderation: Check prompt for profanity.
    2. Retrieval: Fetch top document chunks from FAISS.
    3. Sentiment: Detect user mood (frustrated, curious, etc.).
    4. Generation: LLM call via NVIDIA NIM.
    """
    query = payload.query
    logger.info(f"User {current_user} query: {query[:50]}...")

    # 1. Moderation
    if not moderation_service.is_content_safe(query):
        return ChatResponse(
            answer=moderation_service.get_rejection_message(),
            emotion="neutral",
            sources=[]
        )

    # Convert Pydantic list of models to dictionary list for RAG service
    history_dicts = [{"role": m.role, "content": m.content} for m in payload.history]

    # 2, 3, 4. Answer via RAG service
    try:
        result = rag_service.answer_query(query, history=history_dicts)
        return ChatResponse(
            answer=result["answer"],
            emotion=result["emotion"],
            sources=result["sources"]
        )
    except Exception as exc:
        logger.error(f"RAG generation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI generation failed. Please verify API key and network."
        )

@router.post("/query/stream")
async def chat_query_stream(
    payload: ChatQuery,
    current_user: str = Depends(dependencies.get_current_user)
):
    """
    RAG Streaming Pipeline:
    1. Moderation check.
    2. Streaming generator: Metadata -> Text Chunks.
    """
    query = payload.query
    logger.info(f"User {current_user} streaming query: {query[:50]}...")

    if not moderation_service.is_content_safe(query):
        def reject():
            yield moderation_service.get_rejection_message()
        return StreamingResponse(reject(), media_type="text/plain")

    history_dicts = [{"role": m.role, "content": m.content} for m in payload.history]

    return StreamingResponse(
        rag_service.stream_answer_query(query, history=history_dicts),
        media_type="text/event-stream"
    )

@router.post("/summarize")
async def summarize_document(
    file: UploadFile = File(...),
    current_user: str = Depends(dependencies.get_current_user)
):
    """Async endpoint to summarize a document directly without indexing."""
    filename = file.filename or "file"
    content = await file.read()
    
    try:
        summary = rag_service.summarize_document(content, filename)
        return {"filename": filename, "summary": summary}
    except Exception as exc:
        logger.error(f"Summarization failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(exc)}"
        )

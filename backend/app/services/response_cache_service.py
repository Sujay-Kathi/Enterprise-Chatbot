"""Semantic Response Cache Service for Enterprise Chatbot."""

import os
from pathlib import Path
from typing import Optional, Dict, List
from loguru import logger
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.core.config import get_settings
from app.services.ingestion_service import _get_embeddings

settings = get_settings()

_response_store: Optional[FAISS] = None

def _get_store() -> Optional[FAISS]:
    """Load the response cache index from disk."""
    global _response_store
    path = Path(settings.response_cache_path)
    if _response_store is None and path.exists() and any(path.iterdir()):
        try:
            _response_store = FAISS.load_local(
                str(path),
                _get_embeddings(),
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            logger.warning(f"Failed to load response cache: {e}")
    return _response_store

def check_cache(query: str, threshold: float = 0.98) -> Optional[Dict]:
    """Semantic lookup for a query in the response cache."""
    store = _get_store()
    if store is None:
        return None
    
    # Exact Match First (Simple check)
    # We could use a simple dict, but FAISS is fast enough.
    
    # Similarity Search with Score (Lower score is better in L2 distance)
    # Langchain FAISS similarity_search_with_relevance_scores or similar
    try:
        results = store.similarity_search_with_score(query, k=1)
        if not results:
            return None
            
        doc, score = results[0]
        # For FAISS L2 distance, 0 is perfect match.
        # Conversion to cos-sim or similar is tricky, but 
        # score < 0.05 is usually extremely similar (95%+).
        if score < 0.03: # High similarity threshold for near-identity
            logger.info(f"[SemanticCache] HIT for '{query}' (score={score:.4f})")
            return {
                "answer": doc.page_content,
                "emotion": doc.metadata.get("emotion"),
                "sources": doc.metadata.get("sources", []),
                "cached": True
            }
    except Exception as e:
        logger.error(f"Error checking cache: {e}")
        
    return None

def save_cache(query: str, answer: str, emotion: str, sources: List[str]):
    """Save a question/answer pair to the semantic cache."""
    global _response_store
    
    embeddings = _get_embeddings()
    doc = Document(
        page_content=answer,
        metadata={
            "query": query,
            "emotion": emotion,
            "sources": sources
        }
    )
    
    path = Path(settings.response_cache_path)
    path.mkdir(parents=True, exist_ok=True)
    
    if _response_store is None:
        _response_store = FAISS.from_documents([doc], embeddings)
    else:
        _response_store.add_documents([doc])
        
    _response_store.save_local(str(path))
    logger.info(f"[SemanticCache] Saved entry for: {query[:50]}...")

def clear_cache():
    """Wipe the response cache when documents change."""
    global _response_store
    path = Path(settings.response_cache_path)
    if path.exists():
        import shutil
        shutil.rmtree(path)
        logger.warning("[SemanticCache] Cache invalidated (cleared) due to knowledge update.")
    _response_store = None

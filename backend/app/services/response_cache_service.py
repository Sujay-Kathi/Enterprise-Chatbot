"""Semantic Response Cache Service for Enterprise Chatbot."""

import os
from pathlib import Path
from typing import Optional, Dict, List
from loguru import logger
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.core.config import get_settings
from app.core.embeddings import get_embeddings

settings = get_settings()

_response_store: Optional[FAISS] = None

def _get_store() -> Optional[FAISS]:
    """Load the response cache index from disk."""
    global _response_store
    path = Path(settings.response_cache_path).absolute()
    
    if _response_store is None:
        if path.exists():
            files = list(path.iterdir())
            if files:
                try:
                    logger.info(f"[SemanticCache] Loading index from {path}")
                    _response_store = FAISS.load_local(
                        str(path),
                        get_embeddings(),
                        allow_dangerous_deserialization=True
                    )
                except Exception as e:
                    logger.warning(f"[SemanticCache] Load fail: {e}")
            else:
                logger.debug(f"[SemanticCache] Empty index dir: {path}")
        else:
            logger.debug(f"[SemanticCache] Index path not found: {path}")
            
    return _response_store

def check_cache(query: str) -> Optional[Dict]:
    """Semantic lookup for a query in the response cache."""
    logger.info(f"[SemanticCache] Checking query: '{query}'")
    store = _get_store()
    if store is None:
        logger.warning("[SemanticCache] MISS: Store not available.")
        return None
    
    try:
        results = store.similarity_search_with_score(query, k=1)
        if not results:
            logger.info(f"[SemanticCache] MISS: Index is empty (k=1 returned nothing).")
            return None
            
        doc, score = results[0]
        # FAISS L2 distance: Lower is closer.
        # Threshold: 0.3 for very similar.
        if score < 0.4: 
            logger.success(f"[SemanticCache] HIT! (score={score:.4f})")
            return {
                "answer": doc.metadata.get("answer"),
                "emotion": doc.metadata.get("emotion"),
                "sources": doc.metadata.get("sources", []),
                "cached": True
            }
        else:
            logger.info(f"[SemanticCache] MISS: Score too high ({score:.4f})")
    except Exception as e:
        logger.error(f"[SemanticCache] Search Error: {e}")
        
    return None

def save_cache(query: str, answer: str, emotion: str, sources: List[str]):
    """Save a question/answer pair to the semantic cache."""
    global _response_store
    
    embeddings = get_embeddings()
    doc = Document(
        page_content=query, # Vectorized part (must be the question)
        metadata={
            "answer": answer, # Stored part
            "emotion": emotion,
            "sources": sources
        }
    )
    
    path = Path(settings.response_cache_path).absolute()
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

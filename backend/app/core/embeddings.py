"""Shared embedding and vector store utilities to avoid circular imports."""

import os
from pathlib import Path
from typing import Optional
from loguru import logger
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import get_settings

settings = get_settings()

_embeddings: Optional[HuggingFaceEmbeddings] = None
_vector_store: Optional[FAISS] = None

def get_embeddings() -> HuggingFaceEmbeddings:
    """Singleton embeddings model (loaded once, reused for all requests)."""
    global _embeddings
    if _embeddings is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings

def get_vector_store(force_reload: bool = False) -> Optional[FAISS]:
    """Load the FAISS index from disk, or return None if not yet created."""
    global _vector_store
    
    if force_reload:
        _vector_store = None
        
    index_path = Path(settings.faiss_index_path)
    if _vector_store is None and index_path.exists() and any(index_path.iterdir()):
        try:
            logger.info("Loading existing FAISS index from disk...")
            _vector_store = FAISS.load_local(
                str(index_path),
                get_embeddings(),
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            _vector_store = None
            
    return _vector_store

def set_vector_store(vector_store: FAISS):
    """Update the singleton vector store (e.g., after ingestion)."""
    global _vector_store
    _vector_store = vector_store

"""Document ingestion service: PDF/TXT → chunks → embeddings → FAISS index."""

import os
from pathlib import Path
from typing import Optional

from loguru import logger
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.core.config import get_settings
from app.core.embeddings import get_embeddings, get_vector_store, set_vector_store
from app.services import response_cache_service

settings = get_settings()

# Singleton embeddings model (loaded once, reused for all requests)
# ── Ingestion Core ────────────────────────────────────────────────────────────
_vector_store = get_vector_store()


def _extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from PDF or TXT file bytes."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        import io
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif ext in (".txt", ".csv"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def ingest_document(file_bytes: bytes, filename: str) -> int:
    """
    Process a document file:
    1. Extract text
    2. Split into chunks
    3. Embed with HuggingFace all-MiniLM-L6-v2
    4. Add to FAISS index (persistent on disk)

    Returns: number of chunks indexed
    """
    global _vector_store

    logger.info(f"Ingesting document: {filename}")

    # 1. Extract
    raw_text = _extract_text(file_bytes, filename)
    if not raw_text.strip():
        raise ValueError("Document appears to be empty or unreadable.")

    # 2. Split
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.create_documents(
        texts=[raw_text],
        metadatas=[{"source": filename}],
    )
    logger.info(f"Split into {len(chunks)} chunks.")

    # 2.5 Save raw text for CAG (Hybrid RAG+CAG)
    raw_docs_dir = Path(settings.raw_docs_path)
    raw_docs_dir.mkdir(parents=True, exist_ok=True)
    with open(raw_docs_dir / f"{filename}.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)
    logger.info(f"Saved raw text copy to {raw_docs_dir / f'{filename}.txt'}")

    # 3 & 4. Embed + Index
    embeddings = get_embeddings()
    index_path = settings.faiss_index_path
    Path(index_path).mkdir(parents=True, exist_ok=True)
    
    _vector_store = get_vector_store()
    if _vector_store is None:
        _vector_store = FAISS.from_documents(chunks, embeddings)
    else:
        _vector_store.add_documents(chunks)

    _vector_store.save_local(index_path)
    set_vector_store(_vector_store)
    logger.success(f"FAISS index saved. Total chunks this session: {len(chunks)}")

    # 5. Invalidate Response Cache (Knowledge changed)
    response_cache_service.clear_cache()

    return len(chunks)

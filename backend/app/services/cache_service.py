"""Cache Management Service for Hybrid RAG+CAG."""

import json
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

def _load_registry() -> Dict[str, bool]:
    registry_path = Path(settings.cache_registry_path)
    if not registry_path.exists():
        return {}
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load cache registry: {e}")
        return {}

def _save_registry(registry: Dict[str, bool]):
    registry_path = Path(settings.cache_registry_path)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save cache registry: {e}")

def get_document_status() -> List[Dict]:
    """Returns all filenames in raw_docs_path with their pinned status."""
    registry = _load_registry()
    raw_docs_dir = Path(settings.raw_docs_path)
    if not raw_docs_dir.exists():
        return []
    
    docs = []
    # Current filenames in storage
    for file_path in raw_docs_dir.glob("*.txt"):
        filename = file_path.stem # original filename (without .txt)
        docs.append({
            "filename": filename,
            "pinned": registry.get(filename, False)
        })
    return docs

def pin_document(filename: str, pin: bool = True):
    """Update cache registry pinning status for filename."""
    registry = _load_registry()
    registry[filename] = pin
    _save_registry(registry)
    logger.info(f"Document '{filename}' pinned: {pin}")

def get_pinned_context() -> str:
    """Concatenate text from all pinned documents for CAG."""
    registry = _load_registry()
    context_parts = []
    raw_docs_dir = Path(settings.raw_docs_path)
    
    for filename, pinned in registry.items():
        if pinned:
            file_path = raw_docs_dir / f"{filename}.txt"
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read().strip()
                        if text:
                            context_parts.append(f"### DEEP KNOWLEDGE: {filename}\n{text}")
                except Exception as e:
                    logger.error(f"Error reading pinned doc {filename}: {e}")
            else:
                logger.warning(f"Pinned document {filename} not found in raw storage.")
    
    return "\n\n---\n\n".join(context_parts) if context_parts else ""

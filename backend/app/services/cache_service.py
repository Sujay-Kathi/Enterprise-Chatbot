"""Cache Management Service for Hybrid RAG+CAG."""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Union
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

def _load_registry() -> Dict[str, Union[bool, dict]]:
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
    """Returns all filenames in raw_docs_path with their heat stats."""
    registry = _load_registry()
    raw_docs_dir = Path(settings.raw_docs_path)
    if not raw_docs_dir.exists():
        return []
    
    docs = []
    # Current filenames in storage
    for file_path in raw_docs_dir.glob("*.txt"):
        filename = file_path.stem
        meta = registry.get(filename, False)
        
        # Normalize legacy bool meta to dict
        if isinstance(meta, bool):
            meta = {"pinned": meta, "usage_count": 0, "last_accessed": 0}
            
        docs.append({
            "filename": filename,
            "pinned": meta.get("pinned", False),
            "usage_count": meta.get("usage_count", 0),
            "last_accessed": meta.get("last_accessed", 0)
        })
    return docs

def pin_document(filename: str, pin: bool = True):
    """Update cache registry pinning status for filename."""
    registry = _load_registry()
    meta = registry.get(filename, {"usage_count": 0, "last_accessed": 0})
    if isinstance(meta, bool):
        meta = {"pinned": pin, "usage_count": 0, "last_accessed": 0}
    else:
        meta["pinned"] = pin
        
    registry[filename] = meta
    _save_registry(registry)
    logger.info(f"Document '{filename}' pinned: {pin}")

def record_access(filename: str):
    """Increment document heat score and auto-refresh pins."""
    registry = _load_registry()
    meta = registry.get(filename, {"pinned": False, "usage_count": 0, "last_accessed": 0})
    
    if isinstance(meta, bool):
        meta = {"pinned": meta, "usage_count": 0, "last_accessed": 0}
    
    meta["usage_count"] += 1
    meta["last_accessed"] = time.time()
    registry[filename] = meta
    
    # Auto-promotion logic: Top 5 by usage
    _auto_refresh_pins(registry)
    _save_registry(registry)

def _auto_refresh_pins(registry: Dict[str, dict]):
    """Automatically pin Top 5 documents by heat score."""
    # Convert all to dicts first
    for k in registry:
        if isinstance(registry[k], bool):
            registry[k] = {"pinned": registry[k], "usage_count": 0, "last_accessed": 0}
            
    # Sort by score: usage_count (weighted by recency if needed)
    sorted_docs = sorted(
        registry.items(), 
        key=lambda x: x[1].get("usage_count", 0), 
        reverse=True
    )
    
    # Top 5 are auto-pinned
    for i, (fname, meta) in enumerate(sorted_docs):
        if i < 5:
            meta["auto_pinned"] = True # track that it was auto-pinned
            meta["pinned"] = True
        else:
            # Only unpin if it was auto-pinned, respect manual pins?
            # For simplicity, let's just do Top 5 absolute for now
            meta["auto_pinned"] = False
            meta["pinned"] = False

def get_pinned_context() -> str:
    """Concatenate text from all pinned documents for CAG."""
    registry = _load_registry()
    context_parts = []
    raw_docs_dir = Path(settings.raw_docs_path)
    
    for filename, meta in registry.items():
        pinned = False
        if isinstance(meta, bool):
            pinned = meta
        elif isinstance(meta, dict):
            pinned = meta.get("pinned", False)
            
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

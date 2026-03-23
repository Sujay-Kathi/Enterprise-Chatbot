"""Document ingestion routes: Upload and index PDF/TXT files."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from loguru import logger
from typing import List

from app.core import dependencies
from app.services import ingestion_service, cache_service

router = APIRouter(prefix="/documents", tags=["Document Ingestion"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: str = Depends(dependencies.get_current_user)
):
    """
    Index a single document: PDF or TXT.
    The file is read into memory, split into chunks, embedded, and added to FAISS.
    """
    filename = file.filename or "unknown"
    logger.info(f"User {current_user} is uploading: {filename}")
    
    # Check extension
    if not filename.lower().endswith((".pdf", ".txt", ".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Please upload a PDF, TXT, or CSV."
        )

    try:
        content = await file.read()
        num_chunks = ingestion_service.ingest_document(content, filename)
        
        return {
            "message": "Document indexed successfully",
            "filename": filename,
            "chunks_added": num_chunks
        }
    except ValueError as val_err:
        logger.error(f"Validation error during ingestion: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as exc:
        logger.error(f"Unexpected error during ingestion: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the document."
        )

@router.get("/status", status_code=status.HTTP_200_OK)
def get_index_status(current_user: str = Depends(dependencies.get_current_user)):
    """Check if the vector store is ready for queries."""
    store = ingestion_service.get_vector_store()
    if store is None:
        return {"status": "empty", "message": "No documents indexed yet."}
    
    return {"status": "ready", "message": "Vector store is active and contains document chunks."}

@router.get("/", status_code=status.HTTP_200_OK)
def list_documents(current_user: str = Depends(dependencies.get_current_user)):
    """List all documents with their pinned cache status."""
    docs = cache_service.get_document_status()
    return {"documents": docs}

@router.post("/pin", status_code=status.HTTP_200_OK)
def pin_document(
    filename: str, 
    pin: bool = True,
    current_user: str = Depends(dependencies.get_current_user)
):
    """Toggle pinning a document to the Hot Context Window (CAG)."""
    cache_service.pin_document(filename, pin)
    return {"message": f"Document '{filename}' pinning set to {pin}"}

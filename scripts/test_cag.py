
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../backend"))

os.environ["NVIDIA_API_KEY"] = "test-key" 
# Use absolute path to project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__) + "/..")

from app.services import cache_service

def test_cag_logic():
    print("Testing CAG Logic...")
    
    # Ensure directories exist
    raw_docs_dir = Path(PROJECT_ROOT) / "data" / "raw_documents"
    raw_docs_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = raw_docs_dir / "test_doc.txt"
    test_file.write_text("This is an enterprise policy.", encoding="utf-8")
    print(f"Created test file: {test_file}")
    
    # Test pinning
    cache_service.pin_document("test_doc", True)
    docs = cache_service.get_document_status()
    print(f"Docs Status: {docs}")
    
    # Test context retrieval
    context = cache_service.get_pinned_context()
    print(f"Pinned Context: '{context}'")
    
    if "enterprise policy" in context.lower():
        print("✅ SUCCESS: CAG context retrieval working.")
    else:
        print("❌ FAILURE: CAG context retrieval failed.")

if __name__ == "__main__":
    test_cag_logic()

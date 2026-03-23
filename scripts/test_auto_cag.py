
import sys
import os
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../backend"))

os.environ["NVIDIA_API_KEY"] = "test-key" 

from app.services import cache_service

def test_auto_cag():
    print("Testing Automated CAG Heat Map...")
    
    # 1. Simulate multiple accesses to a doc
    doc_name = "test_doc"
    print(f"Recording 3 accesses for '{doc_name}'...")
    for _ in range(3):
        cache_service.record_access(doc_name)
    
    # 2. Add a new doc to see if it doesn't get pinned automatically yet 
    # (since we only pin top 5)
    doc_b = "cold_doc"
    print(f"Creating '{doc_b}' with 1 access...")
    cache_service.record_access(doc_b)
    
    # Check status
    docs = cache_service.get_document_status()
    for d in docs:
        print(f"-> {d['filename']}: usage={d.get('usage_count')}, pinned={d.get('pinned')}")
    
    # Check CAG context
    context = cache_service.get_pinned_context()
    print(f"Pinned Context (should include test_doc): '{context[:50]}...'")

if __name__ == "__main__":
    test_auto_cag()

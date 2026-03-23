
import sys
import os
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../backend"))

os.environ["NVIDIA_API_KEY"] = "test-key" 

from app.services import response_cache_service

def test_response_cache():
    print("Testing Semantic Response Cache...")
    
    # Clear first for clean test
    response_cache_service.clear_cache()
    
    q = "What is the policy for remote work?"
    a = "Our remote work policy is very flexible."
    
    # 1. Save to cache
    print(f"Saving query: '{q}'")
    response_cache_service.save_cache(q, a, "neutral", ["policy.txt"])
    
    # 2. Exact match check
    print("Checking Exact Match...")
    hit = response_cache_service.check_cache(q)
    if hit:
        print(f"✅ Exact HIT: {hit['answer']}")
    else:
        print("❌ Exact MISS")
        
    # 3. Semantic match check (slight variation)
    q2 = "What is the remote working policy?"
    print(f"Checking Semantic Match for: '{q2}'")
    hit2 = response_cache_service.check_cache(q2)
    if hit2:
        print(f"✅ Semantic HIT: {hit2['answer']}")
    else:
        print("❌ Semantic MISS (Score threshold might be too strict?)")
        
    # 4. Invalidation check
    print("Testing Invalidation...")
    response_cache_service.clear_cache()
    hit3 = response_cache_service.check_cache(q)
    if not hit3:
        print("✅ Invalidation SUCCESS: Cache cleared.")
    else:
        print("❌ Invalidation FAILED")

if __name__ == "__main__":
    test_response_cache()

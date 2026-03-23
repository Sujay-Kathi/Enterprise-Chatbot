# Implementation Plan: Semantic Hybrid Response Cache

## Overview
This plan implements **Response Caching** (exact-match hash + semantic similarity) on top of our existing RAG+CAG structure. It will store user queries and the resulting LLM answers in a dedicated FAISS index. If a new query is >0.98 similar (semantically identical) to a past query, the system will return the cached answer instantly, bypassing the NVIDIA NIM API.

## Success Criteria
- [ ] Sub-50ms response time for cached queries.
- [ ] Accurate semantic matching (correct Answer for "How do I log in?" vs "How to login?").
- [ ] **Cache Invalidation**: Automatic clearing when new documents are uploaded (to prevent stale answers).
- [ ] Streamlit UI displays a "⚡ Cached Answer" badge for transparency.
- [ ] Token usage for repeat common questions is reduced by 100%.

---

## Tech Stack
- **Direct Lookup**: Dictionary-based exact match.
- **Semantic Store**: Dedicated FAISS index for query embeddings (`data/response_cache`).
- **Embedding Model**: Shared `all-MiniLM-L6-v2`.

---

## Task Breakdown

### Phase 1: Response Cache Service (P0)
**Agent**: `backend-specialist` | **Skill**: `python-patterns`

- **Task 1.1: Create `response_cache_service.py`**
  - logic to load/save a dedicated FAISS index for `Questions -> Answers`.
  - Implement `check_cache(query)` with a 0.98 similarity threshold.
  - Implement `save_cache(query, answer, emotion, sources)`.
- **Task 1.2: Add `clear_cache()` logic**
  - Delete/Reset the response cache when `ingestion_service` finishes a new document.
- **Task 1.3: Update `config.py`**
  - Add `settings.response_cache_path = "./data/response_cache"`.
  **VERIFY**: Check directory creation in `data/`.

### Phase 2: Generation Integration (P1)
**Agent**: `backend-specialist` | **Skill**: `api-patterns`

- **Task 2.1: Hook Cache into `rag_service.py`**
  - In `answer_query()` and `stream_answer_query()`, first call `check_cache()`.
  - If a hit: return the cached object immediately.
  - If a miss: Call NVIDIA NIM, then `save_cache()` the new answer.
- **Task 2.2: Preserve Metadata (Emotion/Sources)**
  - Ensure the cache stores the original emotion and source list.
  **VERIFY**: Ask the same question twice and observe the instant response on the 2nd time.

### Phase 3: UI Feedback (P2)
**Agent**: `frontend-specialist` | **Skill**: `frontend-design`

- **Task 3.1: "⚡ Cached" Badge**
  - In the Streamlit chat view, add an indicator if a message was retrieved from the cache.
  **VERIFY**: UI displays "Answer served from cache ⚡".

---

## Phase X: Verification
- [ ] Measure latency difference (ms).
- [ ] `security_scan.py` passes.
- [ ] `test_auto_cag.py` continues to work (Heat map scoring still increments for cache hits?).
  **NOTE**: We should decide if "Cache Hits" increment the Heat Map for documents. (Answer: YES, for consistency).
- [ ] Push to git.

---
## ✅ PHASE X COMPLETE
- Status: **PLANNING COMPLETE**
- Approval Needed: **Yes**

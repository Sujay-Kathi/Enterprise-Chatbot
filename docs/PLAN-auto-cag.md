# Implementation Plan: Automated CAG Promotion (Heat Map)

## Overview
This plan upgrades the CAG (Context-Augmented Generation) system to be **self-optimizing**. Instead of manual pinning, the system will track retrieval frequency ("Heat") for every document. "Hot" documents are automatically promoted to the LLM's active context window for zero-latency, high-accuracy reasoning, while "Cold" documents reside only in FAISS.

## Success Criteria
- [ ] Retrieval of a document snippet via RAG increments its "Heat" score.
- [ ] Top 5 documents by "Heat" are automatically pinned to the CAG context for every request.
- [ ] The Streamlit UI displays a "🔥 Trending" badge on top documents.
- [ ] System automatically "evicts" old context if a document hasn't been used in 24 hours (TTL).
- [ ] Response latency for trending topics is minimized.

---

## Task Breakdown

### Phase 1: Dynamic Heat Tracking (P0)
**Agent**: `backend-specialist` | **Skill**: `python-patterns`

- **Task 1.1: Update `cache_registry.json` Schema**
  - Add `usage_count` (int) and `last_accessed` (timestamp) for each document.
- **Task 1.2: Implement `record_access(filename)` in `cache_service.py`**
  - Increment count and update timestamp.
- **Task 1.3: Update `rag_service.py` to notify accesses**
  - In `answer_query` and `stream_answer_query`, loop through the `sources` used and call `cache_service.record_access()`.
  **VERIFY**: Check `cache_registry.json` after a few queries to see counts increasing.

### Phase 2: Automated Pinning Logic (P1)
**Agent**: `backend-specialist` | **Skill**: `api-patterns`

- **Task 2.1: Implement `refresh_pins()` in `cache_service.py`**
  - Sort documents by (Count * Decay / LastAccessed).
  - Automatically update `pinned=True` for top 5, `pinned=False` for others.
- **Task 2.2: Hook `refresh_pins()` into Ingestion & Queries**
  - Ensure the "Hot Context" is always fresh.
  **VERIFY**: Pinning status changes automatically based on query activity.

### Phase 3: Frontend Visualization (P2)
**Agent**: `frontend-specialist` | **Skill**: `frontend-design`

- **Task 3.1: "Trending Knowledge" Badge**
  - In the sidebar, add a "🔥 Trending" or "⚡ Cached" badge next to documents that are automatically pinned.
- **Task 3.2: Heat Analytics UI**
  - Show the "Access Count" for each document in the library.
  **VERIFY**: UI correctly reflects the dynamic state of the cache.

---

## Phase X: Verification
- [ ] Verify Decay Factor handles old data (preventing permanent "zombie" pins).
- [ ] `security_scan.py` passes.
- [ ] Push to git.

---
## ✅ PHASE X COMPLETE
- Status: **PLANNING COMPLETE**
- Approval Needed: **Yes**

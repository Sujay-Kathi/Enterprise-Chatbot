# Implementation Plan: Tiered Context Architecture (Hybrid RAG+CAG)

## Overview
This plan implements a hybrid architecture combining **RAG (Retrieval-Augmented Generation)** with **CAG (Context-Augmented Generation)**. We will use **Prompt Caching** (via NVIDIA NIM and Stable Prompts) to keep high-priority "Hot Data" (SOPs, Pinned Docs) in the LLM's active context, while using FAISS retrieval for "Cold Data" (the broader document archive).

## Project Type
**WEB & BACKEND** (FastAPI + Streamlit)

---

## Success Criteria
- [ ] Users can "Pin" documents to the active cache via the UI.
- [ ] Pinned context is automatically included in every prompt to ensure 100% accuracy for core documents.
- [ ] FAISS retrieval continues to supplement answers with "Cold" document snippets.
- [ ] The system accurately reports "Context Window Usage" (0-128k tokens).
- [ ] Latency for queries involving pinned docs is minimized via implicit prompt caching.

---

## Tech Stack
- **Caching Logic**: JSON-based meta-registry (`data/cache_registry.json`).
- **Token Counting**: `tiktoken` or `langchain-core` length estimates.
- **LLM**: Llama 3.1 8B (NVIDIA NIM) - Supports 128k context.
- **Backend**: FastAPI.
- **Frontend**: Streamlit.

---

## File Structure Changes
```text
/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── document_routes.py (Add /list and /pin endpoints)
│   │   ├── services/
│   │   │   ├── rag_service.py (Update to handle Tiered Context)
│   │   │   └── cache_service.py (NEW: Manage pinned context state)
├── data/
│   └── cache_registry.json (NEW: Persist pinned state)
```

---

## Task Breakdown

### Phase 1: Backend Foundation (P0)
**Agent**: `backend-specialist` | **Skill**: `api-patterns`

- **Task 1.1: Create Cache Registry Service**
  - Implement `cache_service.py` to manage `data/cache_registry.json`.
  - Methods: `pin_document(filename)`, `unpin_document(filename)`, `get_pinned_content()`.
  - **VERIFY**: Unit test `cache_service` to ensure JSON persistence.

- **Task 1.2: Update Document API Endpoints**
  - Modify `document_routes.py` to add `GET /documents` (list with status) and `POST /documents/pin`.
  - **VERIFY**: Use `curl` to pin a document and check the registry.

### Phase 2: Hybrid RAG Logic (P1)
**Agent**: `backend-specialist` | **Skill**: `python-patterns`

- **Task 2.1: Implement Tiered Prompt Construction**
  - In `rag_service.py`, modify `answer_query` and `stream_answer_query`.
  - Step 1: Fetch all "Pinned" document text from `cache_service`.
  - Step 2: Inject into `SystemMessage` as "CORE_COMPANY_KNOWLEDGE".
  - Step 3: Append FAISS-retrieved "COLD_CONTEXT" as before.
  - **VERIFY**: Log the system prompt length to ensure it stays within 128k tokens.

### Phase 3: Frontend - Knowledge Manager (P2)
**Agent**: `frontend-specialist` | **Skill**: `frontend-design`

- **Task 3.1: Document Management UI**
  - Add a "Knowledge Library" section in the Streamlit sidebar.
  - Display a table of files with a "📌 Cache" toggle.
  - Add a progress bar: "🔥 Cache Usage: [████░░░░░░] 24%".
  - **VERIFY**: Toggling a document correctly updates the backend and refreshes the UI.

### Phase 4: Final Polish & Verification (P3)
**Agent**: `test-engineer` | **Skill**: `webapp-testing`

- **Task 4.1: End-to-End Latency Test**
  - Measure response time differences between cached and non-cached documents.
- **Task 4.2: Accuracy Audit**
  - Ask specific niche questions from pinned docs to ensure 100% recall.
- **Task 4.3: Security & Lint**
  - Run `security_scan.py` and `lint_runner.py`.

---

## Phase X: Verification Checklist
- [ ] No purple/violet hex codes in Streamlit.
- [ ] Token count logic handles edge cases (Empty files, Large files).
- [ ] Prompt Caching stability: EnsurePinned Context is always at the START of the prompt.
- [ ] `security_scan.py` passes.
- [ ] Push all changes to git.

---
## ✅ PHASE X COMPLETE
- Status: **PLANNING COMPLETE**
- Approval Needed: **Yes**

# Project Plan: Enterprise RAG Chatbot

## Overview
This plan outlines the architecture and implementation tasks for the Enterprise RAG Chatbot. 
Based in our PRD and SRS, the system is an AI assistant supporting document ingestion, semantic search via local embeddings, and generation using NVIDIA NIM (Llama 3.1 8B). It is split into a robust FastAPI backend and a Streamlit frontend, deployed via Docker Compose onto an Azure Ubuntu VM to preserve local FAISS indices.

## Project Type
**WEB & BACKEND** (FastAPI API + Streamlit Frontend)

## Success Criteria
- [ ] Users can authenticate via 6-digit OTP to email.
- [ ] Users can upload PDFs and TXT files.
- [ ] Documents chunked, embedded via `all-MiniLM-L6-v2`, and stored in FAISS locally.
- [ ] Chat queries retrieve context and pass to `meta/llama-3.1-8b-instruct` via LangChain.
- [ ] Responses exhibit high empathy and summarize context accurately within 5 seconds.
- [ ] Docker Compose correctly orchestrates both services on an Azure VM.

## Tech Stack
- **Backend**: Python 3.10+, FastAPI, Uvicorn (Robust ASGI performance)
- **Frontend**: Streamlit
- **AI/ML**: LangChain, SentenceTransformers, FAISS-CPU
- **APIs**: NVIDIA NIM Integration (`langchain-nvidia-ai-endpoints`)
- **Deployment**: Docker + Docker Compose (Targeted for Azure VM)

## File Structure
```text
/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py
│   │   │   ├── chat_routes.py
│   │   │   └── document_routes.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── dependencies.py
│   │   │   └── security.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── email_service.py
│   │       ├── ingestion_service.py
│   │       ├── moderation_service.py
│   │       └── rag_service.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│   └── faiss_index/
├── .env.example
└── docker-compose.yml
```

## Task Breakdown

### Task 1: Initialize Project Structure & Environments ✅ DONE
- **Agent**: `orchestrator`
- **Skills**: `app-builder`
- **Priority**: P0
- **INPUT**: Empty directory
- **OUTPUT**: Folder skeletons, initial requirements.txt, and .env templates
- **VERIFY**: Project structure matches the layout above.

### Task 2: Implement Core Authentication (OTP & JWT) ✅ DONE
- **Agent**: `backend-specialist`
- **Skills**: `api-patterns`, `python-patterns`
- **Priority**: P1
- **INPUT**: FastAPI initialization
- **OUTPUT**: `/login` and `/verify-otp` endpoints working. JWT generation logic.
- **FILES**: `core/security.py`, `core/dependencies.py`, `api/auth_routes.py`, `services/email_service.py`

### Task 3: Vector Store & Ingestion Pipeline ✅ DONE
- **Agent**: `backend-specialist`
- **Skills**: `api-patterns`
- **Priority**: P1
- **INPUT**: Uploaded PDF
- **OUTPUT**: PyPDF chunking -> SentenceTransformers -> FAISS Index logic & `/upload-document` endpoint.
- **FILES**: `services/ingestion_service.py`, `api/document_routes.py`

### Task 4: NVIDIA NIM LangChain Integration (RAG Logic) ✅ DONE
- **Agent**: `backend-specialist`
- **Skills**: `api-patterns`
- **Priority**: P1
- **INPUT**: User Query + FAISS History Context
- **OUTPUT**: `ChatNVIDIA` chain that fetches context, adapts emotional tone, and returns response at `/chat` and `/summarize`.
- **FILES**: `services/rag_service.py`, `services/moderation_service.py`, `api/chat_routes.py`

### Task 5: Build Streamlit Frontend UI ✅ DONE
- **Agent**: `frontend-specialist`
- **Skills**: `frontend-design`
- **Priority**: P2
- **INPUT**: Working Backend APIs
- **OUTPUT**: Streamlit dashboard with Login view, Upload Document view, and Chat view.
- **FILES**: `frontend/app.py`

### Task 6: Docker Compose Orchestration ✅ DONE
- **Agent**: `devops-engineer`
- **Skills**: `bash-linux`
- **Priority**: P3
- **INPUT**: Complete source code
- **OUTPUT**: Two Dockerfiles and one `docker-compose.yml` that networks Streamlit to FastAPI and mounts `/data` to the local azure VM file system.
- **FILES**: `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`

## Phase X Verification
- [ ] No purple/violet hex codes used in Streamlit UI
- [ ] Docker Compose boots cleanly
- [ ] Security scan passes locally
- [ ] FAISS persists properly upon container restart

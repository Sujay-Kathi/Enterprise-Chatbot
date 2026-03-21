# Context Document

## Project Overview
This project is an Enterprise RAG (Retrieval-Augmented Generation) Chatbot. It utilizes LangChain to orchestrate LLM processes, with generative inference offloaded to NVIDIA NIM API.

## Current State
- **Phase**: Implementation. Project structure, PRD, and SRS are finalized.
- **Next Steps**: Backend implementation (Auth, Ingestion, RAG), then Frontend, then Docker.

## Architecture
- **Backend Framework**: FastAPI (Python)
- **Frontend Framework**: Streamlit (Python)
- **RAG Orchestrator**: LangChain
- **Embeddings Model**: HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (Local, 100% Free)
- **Vector Database**: FAISS-CPU (Local disk-based, 100% Free)
- **LLM**: Llama 3.1 8B (`meta/llama-3.1-8b-instruct` via NVIDIA NIM API)

## Key Decisions
- **Hybrid Approach**: Embeddings run locally on CPU (free). LLM generation offloaded to NVIDIA NIM API for speed.
- **FAISS over ChromaDB**: Chosen for raw speed and simplicity in a Docker volume mount scenario.
- **Docker Compose**: Two separate containers (backend + frontend) for isolation and independent scaling.
- **Azure VM**: Deployment target is an Ubuntu Linux IaaS VM on Azure (ON HOLD).
- FastAPI backend provides an API boundary separating the Streamlit prototype, making it easy to swap Streamlit for React/Next.js later.

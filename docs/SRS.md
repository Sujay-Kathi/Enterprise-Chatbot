# Software Requirements Specification (SRS)

## 1. Introduction
This document outlines the technical specifications for an Enterprise RAG Chatbot.

## 2. System Architecture
The software comprises two main services:
1. **API Server (Backend)**: Built with FastAPI, handling file ingestion, text processing, embedding, database querying, and LLM communication.
2. **Web Client (Frontend)**: Built with Streamlit, handling the user interface and HTTP communication with the API.

## 3. Technology Stack
- **Languages**: Python 3.10+
- **Frameworks**: FastAPI, Streamlit, LangChain
- **Libraries**:
  - `faiss-cpu` (Vector Store)
  - `sentence-transformers` (Embeddings: all-MiniLM-L6-v2)
  - `langchain-community`, `langchain-core`
  - `langchain-nvidia-ai-endpoints` (NVIDIA NIM Integration)
  - `python-multipart` (File Uploads)
  - `uvicorn` (ASGI Server)
- **External Apis**: NVIDIA NIM API (Model: `meta/llama-3.1-8b-instruct`). Local execution strictly for embeddings.

## 4. Functional Requirements
### FR1: Document Upload Endpoint
- **Method**: POST `/upload-document`
- **Payload**: `multipart/form-data` with files.
- **Action**: Read the file, extract text via PyPDF, split into chunks, generate embeddings, push to FAISS DB.
- **Response**: Success message with indexed chunk count.

### FR2: Chat Query Endpoint & RAG Logic
- **Method**: POST `/chat`
- **Payload**: JSON containing `{"query": "User's question", "history": [{"role": "user", "content": "..."}, ...] }`
- **RAG Logic Execution**:
  1. **Pre-processing (Guardrails)**: Validate the incoming query using a bad language/profanity detection mechanism. Reject the prompt gracefully if inappropriate content is found.
  2. **Query Processing**: Convert the incoming question into an embedding using HuggingFace.
  3. **Retrieval**: Perform a semantic search on FAISS to fetch the top 3-4 most relevant text chunks.
  4. **Prompt Construction**: Combine the user's conversational history, the retrieved chunks (context), and the new question into a LangChain Prompt Template. The prompt will include strict instructions to analyze the user's emotion (e.g., frustrated, confused, happy) and adapt the response tone accordingly using empathy.
  5. **Generation**: Send this engineered prompt to Llama 3.1 8B (`meta/llama-3.1-8b-instruct` via NVIDIA NIM API).
- **Response**: Text answer streamed or returned to the client.

### Integration Mechanism
- **Decoupled Architecture**: The Chatbot Logic resides entirely in the Python backend (FastAPI). 
- **Frontend Integration**: Streamlit (or any future UI like React/Next.js) integrates by simply making HTTP POST requests to the FastAPI endpoints (`/upload-document` and `/chat`). The frontend is just a "dumb" visual layer holding the state, while the backend holds all AI logic.

### FR3: Document Summarization Endpoint
- **Method**: POST `/summarize`
- **Payload**: Form-data with document OR target document ID.
- **Action**: Uses LangChain summarization chains to process and condense large documents via Llama 3.1 8B (`meta/llama-3.1-8b-instruct` via NVIDIA NIM).
- **Response**: Summary text.

### FR4: Authentication Endpoints (2FA)
- **Method**: POST `/login` & POST `/verify-otp`
- **Payload**: Email address (request), Email + OTP (verify).
- **Action**: Sends a 6-digit OTP to the employee's email. Verifies the OTP and issues a JWT token for secure access to protected endpoints (chat, upload, summarize).
- **Response**: JWT access token.

## 5. Non-Functional Requirements
- **Performance**: Response time < 5 seconds. Embeddings generation should process at a rate of at least 50 pages per minute locally.
- **Scalability & Concurrency**: Backend must run via an ASGI server (Uvicorn with Gunicorn workers) capable of handling a minimum of 5 concurrent users simultaneously without blocking the main event thread. High availability architectural design.
- **Security**: Confidential internal documents are never used for public LLM training. APIs are secured by JWT (2FA).
- **Cost & Constraints**: Uses free local embeddings to save costs. Generative tasks are offloaded to NVIDIA NIM API (Requires API Key). The base FastAPI server should easily run on standard/low-end hardware since AI computation is offloaded.
- **Deployment**: Targeted for an Azure Virtual Machine (Ubuntu Linux IaaS). The application will be deployed using Docker/Docker Compose to guarantee environment consistency and ensure fast local disk I/O for FAISS.("ON HOLD!!")

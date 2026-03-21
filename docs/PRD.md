# Product Requirements Document (PRD)

## 1. Product Vision
**Goal**: Build a production-ready AI assistant that improves organizational efficiency by automating information retrieval and document understanding.
This is a zero-cost, highly-efficient enterprise chatbot that helps employees retrieve information related to HR policies, IT support, company procedures, and internal documentation. It allows users to upload these confidential documents and converse with an AI regarding them securely.

## 2. Target Audience
- Employees and stakeholders who need quick insights from dense PDF, Word, or TXT documents.
- Developers aiming to extend the system with more robust frontend solutions in the future.

## 3. Core Features 
- **Document Ingestion**: Users can upload multiple file types (PDF, TXT, CSV) through a simple UI.
- **Semantic Search**: Text chunks are embedded and stored efficiently (FAISS) to be retrieved with high relevance based on user questions.
- **Conversational AI**: Uses State-of-the-Art Llama 3 models capable of handling context-rich prompts (via Groq or NVIDIA NIM APIs).
- **Authentication (2FA)**: Secure user access via an Email-based OTP (One Time Password) login system.
- **Content Moderation**: Built-in bad language and profanity detection to block abusive or inappropriate queries gracefully.
- **Emotion-Aware Responses**: The chatbot detects user emotion (e.g., frustration, curiosity) from their query and adjusts its tone and response style accordingly.
- **Document Processing**: Supports document processing use cases including automatic summarization and keyword extraction.
- **Multi-user Support**: Designed to be scalable and handle a minimum of 5 concurrent users simultaneously.
- **Cost-Effective**: Operates completely free of cost by leveraging free-tier APIs (Groq or NVIDIA NIM), local FAISS storage, and local embeddings.
- **Decoupled Architecture**: Separation of backend (FastAPI) and frontend (Streamlit) for high scalability on standard hardware/cloud.

## 4. Future Additions / Roadmap
- **User Authentication**: Secure access using JWT tokens.
- **Document Management**: UI to view, delete, and manage uploaded data sources.
- **Citation/Source References**: Display exactly which document chunk answered the user's question.
- **Streaming UI**: Token-by-token text generation rendering on the frontend.

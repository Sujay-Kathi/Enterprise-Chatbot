"""
Vercel entry point for the Enterprise RAG Chatbot API.

Vercel requires the FastAPI `app` object at module level in the api/ folder.
This file bridges the gap by adding the backend/ directory to sys.path
so that backend's relative imports (e.g. 'from app.api') work correctly.
"""

import os
import sys

# --- Path Setup ---
# api/main.py is at: project_root/api/main.py
# backend/      is at: project_root/backend/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_path = os.path.join(project_root, "backend")

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# --- Import FastAPI App ---
# This imports `app` from backend/main.py
from main import app  # noqa: F401, E402

# Vercel detects this `app` object automatically.

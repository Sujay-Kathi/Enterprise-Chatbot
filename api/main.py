import os
import sys

# Get the absolute path of the current file (api/main.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# The backend directory is a sibling to the api directory in the project root
# project_root/
# ├── api/main.py
# └── backend/
#     ├── main.py  # original app
#     └── app/     # code package
project_root = os.path.dirname(current_dir)
backend_path = os.path.join(project_root, "backend")

# Add the backend directory to sys.path so we can import from it
# and so that backend's relative imports (like 'from app.api') continue to work.
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import the FastAPI application instance from frontend-chatbot/backend/main.py
from main import app

# Vercel needs this 'app' object to be present in this module level.

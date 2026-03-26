# --- Build / Runtime Stage ---
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for PDF parsing/FAISS)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from project root and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./backend/app ./app
COPY ./backend/main.py ./main.py

# Create data directory for FAISS (will be mounted as volume on Render)
RUN mkdir -p /data/faiss_index

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

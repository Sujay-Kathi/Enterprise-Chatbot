# --- Build / Runtime Stage ---
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy only frontend requirements (lean — no backend deps)
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Streamlit app code
COPY frontend/app.py .

# Expose Streamlit port
EXPOSE 8501

# Streamlit config: disable telemetry, set headless mode for containers
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

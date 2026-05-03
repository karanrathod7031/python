FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend/pyproject.toml backend/
COPY backend/app backend/app
COPY backend/cli.py backend/
COPY plugins plugins/
COPY .env.example .env

# Install Python dependencies
RUN pip install --no-cache-dir -e backend/

# Create data directories
RUN mkdir -p data logs

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]

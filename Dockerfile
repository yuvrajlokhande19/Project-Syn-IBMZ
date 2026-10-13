# Multi-stage lightweight s390x compatible Dockerfile for Project Syn
FROM python:3.10-slim-bullseye

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY 03-mainframe-core/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose API port
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# Run Uvicorn Mainframe Core
CMD ["python3", "-m", "uvicorn", "main:app", "--app-dir", "03-mainframe-core", "--host", "0.0.0.0", "--port", "8000"]

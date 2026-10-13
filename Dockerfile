# Native IBM LinuxONE s390x Dockerfile for Project Syn
FROM ubuntu:22.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install pre-compiled s390x binaries for python, numpy, pandas, sqlite, and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-pandas \
    python3-numpy \
    python3-requests \
    curl \
    sqlite3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install remaining pure-python packages (FastAPI, uvicorn, pydantic)
COPY 03-mainframe-core/requirements.txt requirements.txt
RUN pip3 install --no-cache-dir fastapi uvicorn pydantic python-dotenv httpx

# Copy application files
COPY . .

# Expose API port
EXPOSE 8000

# Run Uvicorn Mainframe Core
CMD ["python3", "-m", "uvicorn", "main:app", "--app-dir", "03-mainframe-core", "--host", "0.0.0.0", "--port", "8000"]

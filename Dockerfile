# syntax=docker/dockerfile:1
FROM python:3.10-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Runtime stage ---
FROM python:3.10-slim

# Platform-agnostic environment setup
ENV PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv

# Copy application code (with .dockerignore in place)
COPY . .

# Create non-root user and permissions
RUN useradd -m appuser \
    && chown -R appuser:appuser /app \
    && mkdir -p /app/tmp \
    && chown appuser:appuser /app/tmp

USER appuser

# Health check (for platforms that support it)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Universal run command
CMD ["sh", "-c", "uvicorn main:app --host $HOST --port $PORT"]
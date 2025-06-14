FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create and set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install wheel && \
    pip install -r requirements.txt

# Create production image
FROM python:3.12-slim

LABEL maintainer="Ansible TinyLlama Team <info@ansibletinyllama.org>"
LABEL description="Ansible-TinyLlama Integration - AI-powered automation"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/yourusername/automation-with-agentic-llm"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ssh \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create necessary directories with proper ownership
RUN mkdir -p /app/models /app/logs /app/config

# Copy the application code
COPY --chown=nobody:nogroup . /app/

# Set proper permissions
RUN chmod -R 755 /app && \
    chmod -R 770 /app/logs

# Expose the API port
EXPOSE 8000

# Create a non-root user and switch to it
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    chown -R appuser:appuser /app/logs /app/models /app/config
USER appuser

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command using gunicorn for production
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--timeout", "120", "--access-logfile", "-", "src.api.rest_api:app"]

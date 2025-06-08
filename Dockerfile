FROM python:3.12-slim

LABEL maintainer="Your Name <your.email@example.com>"
LABEL description="Ansible-TinyLlama Integration - AI-powered automation"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Create and set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    ssh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p models logs

# Expose the API port
EXPOSE 8000

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Default command
CMD ["python", "-m", "src.main", "api", "--host", "0.0.0.0", "--port", "8000"]

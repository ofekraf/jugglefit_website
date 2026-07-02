# Use official Python base image
FROM python:3.11-slim

LABEL authors="ofekrafaeli"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Set working directory
WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (changes least frequently)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (changes most frequently)
# This layer will be invalidated on any code change, but dependencies above will be cached
COPY . .

# Create non-root user and database directory with correct permissions
RUN adduser --disabled-password --gecos '' --uid 1001 appuser && \
    mkdir -p /app/database_data && \
    chown -R appuser:appuser /app
USER appuser

# Expose Flask port
EXPOSE 5001

# Container-level health check (also declared in docker-compose.prod.yml)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Production entrypoint. Dev override lives in docker-compose.yml.
CMD ["gunicorn", "--bind", "0.0.0.0:5001", \
     "--workers", "2", "--threads", "4", "--preload", \
     "--timeout", "60", "--max-requests", "2000", "--max-requests-jitter", "200", \
     "wsgi:app"]

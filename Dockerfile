# syntax=docker/dockerfile:1

# Base stage - common dependencies
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base AS dev

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code (will be overridden by volume in dev)
COPY . .

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Development command with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM python:3.12-slim AS prod

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only production requirements
COPY requirements.txt ./

# Install only production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Production command with Gunicorn
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

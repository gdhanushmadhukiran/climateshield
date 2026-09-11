# ClimateShield FastAPI Backend Container
FROM python:3.12-slim

# Install system dependencies including libpq for PostgreSQL/PostGIS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and Alembic configurations
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY .env.example .env

# Expose port
EXPOSE 8000

# Health check against root liveness endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

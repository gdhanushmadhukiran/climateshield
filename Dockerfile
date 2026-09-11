# ClimateShield Production Container for Render
FROM python:3.12-slim

# Install system dependencies including libpq for PostgreSQL/PostGIS and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY shield-core-vis-main/shield-core-vis-main/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy application source code, Alembic configurations, and ML models
COPY shield-core-vis-main/shield-core-vis-main/backend/app/ ./app/
COPY shield-core-vis-main/shield-core-vis-main/backend/ml_models/ ./ml_models/
COPY shield-core-vis-main/shield-core-vis-main/backend/alembic/ ./alembic/
COPY shield-core-vis-main/shield-core-vis-main/backend/alembic.ini ./alembic.ini
COPY shield-core-vis-main/shield-core-vis-main/backend/.env.example ./.env

# Expose port (Render dynamically sets $PORT)
ENV PORT=8000
EXPOSE 8000

# Health check against root liveness endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start Uvicorn server respecting dynamic $PORT from Render
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"

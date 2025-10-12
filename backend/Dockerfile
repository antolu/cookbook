# Multi-stage Dockerfile for both development and production builds
ARG BUILD_TYPE=production

# Base stage with common dependencies
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install base system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base AS development
# Install additional dev packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install dev tools for hot reload
RUN pip install --no-cache-dir watchfiles==0.24.0

# Production stage
FROM base AS production
# Install additional production packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app user for production
RUN groupadd -r app && useradd -r -g app app

# Final stage selection based on build type
FROM ${BUILD_TYPE} AS final

# Copy pyproject.toml first to leverage Docker layer cache
COPY backend/pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .[dev,test]

# Copy application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p uploads compressed

# Set ownership for production
ARG BUILD_TYPE=production
RUN if [ "$BUILD_TYPE" = "production" ]; then \
        chown -R app:app /app; \
    fi

# Switch to app user in production
RUN if [ "$BUILD_TYPE" = "production" ]; then \
        USER app; \
    fi

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set command based on build type
ARG BUILD_TYPE=production
RUN if [ "$BUILD_TYPE" = "development" ]; then \
        printf '#!/bin/bash\nexec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload\n' > /start.sh && \
        chmod +x /start.sh; \
    else \
        printf '#!/bin/bash\nexec uvicorn app.main:app --host 0.0.0.0 --port 8000\n' > /start.sh && \
        chmod +x /start.sh; \
    fi

# Use the dynamically created start script
ENTRYPOINT ["/start.sh"]

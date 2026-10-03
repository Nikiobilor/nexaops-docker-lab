# =============================================================================
# NexaOps Internal Dashboard — Production Dockerfile
# Multi-stage build: builder stage installs deps, final stage runs the app
# =============================================================================

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
# Install dependencies in a separate stage so build tools
# don't end up in the final image
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /build

# Install build dependencies (only needed at build time)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy only requirements first — Docker caches this layer
# If requirements.txt hasn't changed, pip install is skipped on rebuild
COPY requirements.txt .

# Install Python dependencies into /install (isolated from system Python)
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Final image ──────────────────────────────────────────────────────
# Start fresh from a clean base — no build tools, no compilers
FROM python:3.11-slim AS final

# Add image metadata
LABEL maintainer="NexaOps Platform Team <devops@nexaops.com>"
LABEL version="1.0.0"
LABEL description="NexaOps Internal Dashboard"
LABEL org.opencontainers.image.source="https://github.com/nexaops/dashboard"

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Create a non-root user to run the application
# -r = system user, -g root = primary group root, no home dir needed
RUN useradd -r -u 1001 -g root -s /bin/false nexaops-app

# Set working directory
WORKDIR /app

# Copy application code
# Copying specific directories avoids including unnecessary files
COPY app/ ./app/
COPY templates/ ./templates/


# Set ownership of app files to the non-root user
RUN chown -R nexaops-app:root /app \
  && chmod -R g=u /app

# Switch to non-root user
USER nexaops-app

# Environment variables with safe defaults
# Secrets (DB_PASSWORD etc.) are NEVER set here — injected at runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    APP_VERSION=1.0.0 \
    ENVIRONMENT=production \
    PORT=5000

# Document which port the app uses
EXPOSE 5000

# Health check — Docker will call this to determine container health
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Use ENTRYPOINT for the executable + CMD for default arguments
# This allows overriding CMD arguments without replacing gunicorn
ENTRYPOINT ["gunicorn"]
CMD ["--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--threads", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app.main:app"]

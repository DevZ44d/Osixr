# ─────────────────────────────────────────────────────────────────
#  Stage 1 — Builder
#  Install deps + package in an isolated layer so the final image
#  stays lean and has no build tools in it.
# ─────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Don't write .pyc files during build, keep output clean
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Copy only what pip needs first (better layer cache)
COPY requirements.txt setup.py ./
COPY osixr/ ./osixr/

# Install into a prefix so we can copy just the installed files later
RUN pip install --upgrade pip --quiet && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt && \
    pip install --prefix=/install --no-cache-dir .


# ─────────────────────────────────────────────────────────────────
#  Stage 2 — Runtime
#  Minimal image — only Python + the installed packages.
# ─────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL maintainer="osixr" \
      description="IP intelligence & EXIF metadata toolkit" \
      version="1.0.0"

# Security: run as non-root user
RUN useradd --create-home --shell /bin/bash osixr

# Pull installed packages from builder
COPY --from=builder /install /usr/local

# Create a workspace directory the user can mount into
RUN mkdir -p /data && chown osixr:osixr /data

# Runtime env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/usr/local/lib/python3.12/site-packages

USER osixr
WORKDIR /data

# Smoke-test: make sure the CLI loads correctly
RUN python -m osixr --help > /dev/null

ENTRYPOINT ["python", "-m", "osixr"]
CMD ["--help"]

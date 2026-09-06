FROM python:3.12-slim

# Install uv directly from their official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy the entire application (including src/)
COPY . .

# Install dependencies using uv (creates a .venv automatically)
RUN uv sync --frozen --no-dev

# Expose port for the FastAPI server
EXPOSE 8000

# Default command (will be overridden by fly.toml processes, but good as a fallback)
CMD ["uv", "run", "start.py", "server"]

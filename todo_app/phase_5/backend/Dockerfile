FROM python:3.13-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev
COPY . .
# Install project
RUN uv sync --frozen --no-dev

FROM python:3.13-slim-bookworm
WORKDIR /app
# Copy environment
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
# Run as non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.13-slim-bookworm AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY . .
RUN uv sync --frozen --no-dev

FROM python:3.13-slim-bookworm
WORKDIR /app
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
RUN useradd -m appuser && chown -R appuser /app
USER appuser
CMD ["python", "src/main.py"]
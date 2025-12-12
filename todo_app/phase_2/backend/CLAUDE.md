# Backend Guidelines

## Build & Run
- Package Manager: `uv`
- Run Dev Server: `uv run uvicorn src.todo_app.main:app --reload --port 8000`
- Run Tests: `uv run pytest`

## Architecture
- Framework: FastAPI
- ORM: SQLModel (Pydantic + SQLAlchemy)
- Structure: `src/todo_app`
  - `routes/`: API endpoints
  - `models.py`: Database models
  - `deps.py`: Dependencies (Auth, DB)
  - `db.py`: Database connection
- Auth: JWT verification (stateless, issued by Better Auth)

## Code Style
- Typed Python (3.12+)
- Pydantic models for all I/O
- No circular imports

## Future Considerations
- Rate Limiting: Implement `slowapi` or similar middleware for API protection.
- Monitoring: Add OpenTelemetry/Prometheus.
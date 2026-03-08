## Cursor Cloud specific instructions

### Project overview

Replify AI Assistant -- React (CRA) frontend + FastAPI (Python) backend + Redis. See `README.md` for standard setup commands.

### Services

| Service | Port | Start command |
|---------|------|---------------|
| Backend (FastAPI) | 8000 | `cd backend && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000` |
| Frontend (React)  | 3000 | `cd frontend && BROWSER=none REACT_APP_API_BASE_URL=$BACKEND_URL npm start` (set BACKEND_URL to the local backend address, port 8000) |
| Redis              | 6379 | `redis-server --daemonize yes` |

### Non-obvious caveats

- **Redis must be running before starting the backend.** The backend creates a global `RedisClient` on import, so it will fail at startup if Redis is unreachable.
- **Frontend proxy in `package.json`** points to a remote production server. For local dev, set the `REACT_APP_API_BASE_URL` env var to the backend's local URL (port 8000) when starting the frontend so API calls hit the local backend.
- **`SKIP_LOGIN=True`** in `backend/.env` bypasses Instagram OAuth and uses a hardcoded test user. Required for local development without real Instagram credentials.
- **Frontend tests** (`npm test`) fail with an ESM/axios compatibility issue. This is a pre-existing issue (default CRA test was never updated for the actual app).
- **Backend has no dedicated test suite.** Verify via `python -m py_compile main.py` and direct API calls to the `/api/v1/health` endpoint.
- **Lint**: Run `npx eslint src/` in the frontend directory. No separate linter is configured for the backend.
- The `backend/.env` file is not committed to the repo. Create it with at minimum `SKIP_LOGIN=True` and `REDIS_HOST=localhost`.

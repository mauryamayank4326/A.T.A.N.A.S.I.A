# M.A.U.R.Y.A.

**Multi-source Analysis for Uncovering Reconnaissance & Yielding Actionable-intel**

Modern OSINT & Threat Recon Dashboard.

## Mission

M.A.U.R.Y.A. is an asynchronous External Attack Surface Management
(EASM) and Cyber Threat Intelligence (CTI) reconnaissance platform.

Longer-term goals include:

- asynchronous network collection;
- modular OSINT workers;
- relational intelligence persistence;
- fault-isolated reconnaissance tasks;
- operational attack-surface visualization;
- structured forensic export.

## Current Status

Development milestone: 0.11.0

Lifecycle: Day 11 / 50

The current implementation provides a FastAPI application with `/health` and
`/api/v1/health` endpoints, asynchronous SQLAlchemy persistence on SQLite,
environment-backed settings, and request ID middleware. Both health endpoints
check database connectivity. Network collection, OSINT workers, visualization,
and forensic export remain longer-term goals.

## Development

The project requires Python 3.10 or later. From the project root, create and
activate a virtual environment, then install the development dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Create a local environment file if you want to override the defaults:

```bash
cp .env.example .env
```

The app reads settings with the `MAURYA_` prefix. By default, it uses
`sqlite+aiosqlite:///./data/osint.db` and serves the versioned health endpoint
at `http://127.0.0.1:8000/api/v1/health`; the root health endpoint is at
`http://127.0.0.1:8000/health`.

Run the app:

```bash
uvicorn app.main:app --reload
```

Run tests and code-quality checks:

```bash
pytest -v
ruff check .
ruff format --check .
```

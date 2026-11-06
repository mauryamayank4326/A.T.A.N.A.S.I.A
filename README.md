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

Development milestone: 0.13.0

Lifecycle: Day 13 / 50

Today's focus: Establish strict, reusable API data contracts with Pydantic v2,
building on the versioned router architecture introduced on Day 12.

Day 12 organized the API into versioned routers and centralized database
dependencies and application lifecycle management. Day 13 adds a schema layer
for validating incoming data and serializing outgoing responses:

- `app/schemas/common.py` defines shared request and ORM-read schema settings.
- `app/schemas/target.py` validates and normalizes target domains and defines
  target response serialization.
- `app/schemas/scan.py` defines scan request and response data contracts.
- `tests/test_schemas.py` covers validation and ORM-style serialization.

The request schemas reject unexpected fields. Target domains are normalized to
lowercase with trailing dots removed, then checked for valid DNS-domain syntax.
Scan requests validate target UUIDs. Read schemas can load ORM attributes;
target UUIDs are serialized as strings.

Roadmap boundary: Day 13 establishes schemas only. It does not implement the
scan endpoint; `/api/v1/scans` is planned for Day 15.

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
`sqlite+aiosqlite:///./data/osint.db` and serves the health endpoint at
`http://127.0.0.1:8000/api/v1/health`. The API prefix defaults to `/api/v1`;
it can be overridden through application settings.

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

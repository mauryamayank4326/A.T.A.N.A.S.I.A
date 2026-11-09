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

Development milestone: 0.15.0

Lifecycle: Day 15 / 50

A scan is the central operational unit of M.A.U.R.Y.A.

Every future reconnaissance operation—subdomain discovery, WHOIS collection, Shodan enrichment, TCP probing, and email harvesting—will be associated with a scan.

Today establishes the API entry point for that lifecycle.

Objectives
1. Accept a target UUID through a validated request.
2. Confirm that the target exists.
3. Create a new scan record.
4. Assign the initial pending status.
5. Persist the record using an asynchronous database session.
6. Return a structured ScanRead response.
7. Use the Day 14 error contract for missing targets and database conflicts.
8. Test successful creation and failure scenarios.
Expected request:
POST /api/v1/scans
Content-Type: application/json


{
  "target_id": "7f7c8f7c-5e2b-4d4c-8f7c-123456789abc"
}


Expected successful response (assuming the target exists):
{
  "id": "generated-scan-uuid",
  "target_id": "7f7c8f7c-5e2b-4d4c-8f7c-123456789abc",
  "status": "pending",
  "started_at": null,
  "completed_at": null
}


The UUID shown for the scan is illustrative; the database model generates the actual identifier.
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

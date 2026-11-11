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

Development milestone: 0.16.0

Lifecycle: Day 16 / 50

Objective: Build an asynchronous WHOIS intelligence service that retrieves and normalizes publicly available domain registration metadata.

The service should extract:
- Registrar information
- Domain creation date
- Domain expiration date
- Last updated date
- Nameservers
- Registrant organization, when available
- Country, when available
- Registration-related email addresses, when available
Scope boundaries
Included today	Deferred to later days
WHOIS lookup	Shodan intelligence
Registration metadata extraction	TCP service scanning
Date normalization	Database persistence
Nameserver extraction	Scan orchestration
Error handling and timeout	Dashboard integration
Async execution	API endpoint integration

We will not modify the database schema or expose a new API endpoint today.
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

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

Development milestone: 0.18.0

Lifecycle: Day 18 / 50

Objective
Create a unified passive reconnaissance service that combines crt.sh and WHOIS intelligence for a single target domain.

The service will:
1. Validate and normalize the target domain.
2. Execute crt.sh and WHOIS lookups concurrently.
3. Collect discovered subdomains.
4. Collect registration metadata.
5. Handle partial source failures.
6. Return a predictable result structure.
7. Remain independent of FastAPI routes and database persistence.
Expected output
For a target such as example.com, the service should produce a result conceptually like:
Target: example.com

Certificate Transparency:
    api.example.com
    www.example.com

WHOIS:
    Registrar: Example Registrar
    Created: 2020-01-01
    Expires: 2030-01-01

Source Status:
    crt.sh: successful
    WHOIS: successful


This is an illustrative output, not a claim about live lookup results.

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

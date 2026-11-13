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

Development milestone: 0.21.0

Lifecycle: Day 21 / 50

Shodan provides indexed information about internet-connected devices and services. It can enrich domain reconnaissance with externally observed host and service information.

Today's objectives:
1. Build an asynchronous Shodan API client using httpx.
2. Read the API key securely from the existing application settings.
3. Validate input before sending requests.
4. Handle authentication failures, rate limits, timeouts, and upstream errors.
5. Normalize returned host information into a predictable structure.
6. Test the client without making live Shodan requests.
7. Keep the service separate from the existing passive collectors.
Scope boundary: Day 21 is API integration and response normalization. Active TCP port probing remains a separate later task. Shodan results are observations from its indexed dataset, not proof of current reachability.

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

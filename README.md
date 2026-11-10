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

Certificate Transparency (CT) logs provide publicly observable records of certificates issued for domain names.

These records can reveal:
- Previously unknown subdomains.
- Development and staging hostnames.
- Authentication and administrative hostnames.
- API and service hostnames.
- Alternative hostnames associated with an organization's domain.
For example, a certificate associated with example.com may contain:
example.com
www.example.com
api.example.com
dev.example.com
staging.example.com
mail.example.com


M.A.U.R.Y.A. will use crt.sh as its first passive subdomain discovery source.
Objectives
1. Create a dedicated reconnaissance service module.
2. Query crt.sh asynchronously using HTTPX.
3. Parse certificate JSON responses.
4. Extract hostnames from certificate records.
5. Normalize wildcard and multiline hostname entries.
6. Validate that discovered names belong to the requested domain.
7. Deduplicate results.
8. Handle network errors, HTTP errors, and malformed responses.
9. Add automated tests using mocked HTTP responses.
Expected output: A normalized collection of subdomains that can later be associated with a persisted scan.

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

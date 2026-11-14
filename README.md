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

Development milestone: 0.23.0

Lifecycle: Day 23 / 50

Day 22 answers:
Is this TCP port accepting connections?

Day 23 aims to answer:
What service appears to be responding on this port?

For example:
Port	TCP status	Possible service
22	Open	SSH
80	Open	HTTP
443	Open	HTTPS
3306	Open	MySQL
5432	Open	PostgreSQL

Port numbers are only hints. A service running on port 8080 might not be HTTP, and a service running on port 443 might not be HTTPS.
Today's objectives
- Extend the existing TCP observation model.
- Capture initial service banners where available.
- Identify common services using conservative heuristics.
- Preserve connection timeout and concurrency controls.
- Handle services that do not send an initial banner.
- Add automated tests using mocked asynchronous streams.
Scope: Basic banner collection and service identification only. No vulnerability exploitation, authentication attempts, brute forcing, or intrusive protocol testing..

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

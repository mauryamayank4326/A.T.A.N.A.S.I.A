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

Development milestone: 0.19.0

Lifecycle: Day 19 / 50

Objective:
Day 18 established concurrent collection and partial-result preservation. Day 19 hardens that integration so the passive reconnaissance layer is safer, more predictable, and ready for API and persistence wiring.

Completed updates:
- Normalized and validated domain handling for both reconnaissance sources.
- Consolidated crt.sh and WHOIS results into a single, serializable `PassiveReconResult`.
- Preserved partial success by recording source failures without dropping successful data.
- Filtered subdomains to unique, sorted, in-scope hostnames only.
- Sanitized source error messages for stable downstream reporting.
- Distinguished empty successful results from failed lookups.
- Expanded the test suite to cover malformed input, source failures, and unexpected exceptions.

Current validation status:
- Passive reconnaissance tests are passing in the project virtual environment.
- The project is ready to move into the next integration phase for API exposure and persistence.

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

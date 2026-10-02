# M.A.U.R.Y.A.

**Multi-source Analysis for Uncovering Reconnaissance & Yielding Actionable-intel**

Modern OSINT & Threat Recon Dashboard.

## Mission

M.A.U.R.Y.A. is an asynchronous External Attack Surface Management
(EASM) and Cyber Threat Intelligence (CTI) reconnaissance platform.

The platform is designed around:

- asynchronous network collection;
- modular OSINT workers;
- relational intelligence persistence;
- fault-isolated reconnaissance tasks;
- operational attack-surface visualization;
- structured forensic export.

## Current Status

Version: 0.4.0

Lifecycle: Day 04 / 50

2. Motive of the day

Day 04 will focus on configuration integrity. M.A.U.R.Y.A. already reads environment-backed settings, but production-oriented software should validate those settings before they reach the database engine, application lifecycle, or future reconnaissance workers.

Today we will:

Normalize environment names and log levels.

Validate the database URL against the chosen async SQLite architecture.

Preserve the API prefix validation.

Keep secrets represented by SecretStr.

Add dedicated configuration tests.

Test boundary conditions instead of only testing successful settings.

Preserve Day 03's lifespan and dependency-injection design.

Out of scope: ORM models, scan routes, collectors, dashboard, and new database functionality.
## Development

Create a virtual environment:

```bash
python3.10 -m venv .venv
```
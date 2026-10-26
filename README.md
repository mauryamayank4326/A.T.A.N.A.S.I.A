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

Version: 0.10.0

Lifecycle: Day 10 / 50

1. Motive of the Day
- Consolidate the existing database initialization and resource lifecycle.
- Verify registration of all five ORM entities.
- Establish isolated database lifecycle tests.
- Validate table creation, foreign-key enforcement, and metadata consistency.
- Confirm that indexes declared in model metadata are created in a fresh database.
- Preserve existing application settings, session-factory behavior, and the configured database.
Day 10 exit goal: a repeatable, testable database foundation that Week 3 can safely use for FastAPI dependency injection and scan creation.

## Development

Create a virtual environment:

```bash
python3.10 -m venv .venv
```

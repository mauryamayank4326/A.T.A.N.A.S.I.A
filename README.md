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

Version: 0.9.0

Lifecycle: Day 09 / 50

Day 09 adds composite indexes for scan-history lookups on scans and reconnaissance observations:

- scans: `(target_id, created_at)`;
- subdomains, exposed ports, and discovered emails: `(scan_id, created_at)`.

The tests verify that these indexes are declared in SQLAlchemy metadata and created in SQLite by schema initialization. They do not measure query performance. Startup initialization creates missing tables but does not migrate existing tables or add indexes to tables that were already created; use a migration when evolving an existing database schema.

## Development

Create a virtual environment:

```bash
python3.10 -m venv .venv
```
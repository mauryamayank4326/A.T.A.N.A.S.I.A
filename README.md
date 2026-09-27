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

Version: 0.3.0

Lifecycle: Day 03 / 50

[ ] Day 02 code reviewed
[x] Unused database import removed
[x] Lifespan settings coupling corrected
[x] create_lifespan() introduced
[x] Custom Settings preserved through lifespan
[x] API dependency package introduced
[x] AsyncSession dependency introduced
[x] Existing WAL configuration preserved
[x] Existing database tests preserved
[x] Lifecycle regression test added
[x] Isolated database testing preserved
[ ] Ruff passes locally
[ ] Pytest passes locally
[ ] Application manually verified
[ ] Git diff reviewed
[ ] Commit created
[ ] Branch pushed
## Development

Create a virtual environment:

```bash
python3.10 -m venv .venv
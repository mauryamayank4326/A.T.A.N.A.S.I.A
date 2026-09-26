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

Version: 0.2.0

Lifecycle: Day 02 / 50

Current milestone:
╔══════════════════════════════════════════════════════╗
║              M.A.U.R.Y.A. — DAY 02                 ║
║             DATABASE FOUNDATION                     ║
╠══════════════════════════════════════════════════════╣
║ ☐ Async SQLAlchemy engine implemented               ║
║ ☐ aiosqlite integration operational                 ║
║ ☐ Declarative Base established                      ║
║ ☐ AsyncSession factory established                  ║
║ ☐ SQLite WAL enabled                                ║
║ ☐ synchronous=NORMAL verified                       ║
║ ☐ Foreign-key enforcement enabled                   ║
║ ☐ SQLite busy timeout configured                    ║
║ ☐ Database directory auto-created                   ║
║ ☐ FastAPI startup initializes database              ║
║ ☐ FastAPI shutdown disposes database                ║
║ ☐ Database connectivity test passes                 ║
║ ☐ WAL configuration test passes                     ║
║ ☐ Session factory test passes                       ║
║ ☐ Existing Day 01 tests still pass                  ║
║ ☐ Ruff passes                                       ║
║ ☐ No database artifacts committed                   ║
║ ☐ Git diff reviewed                                 ║
║ ☐ Conventional commit created                       ║
╚══════════════════════════════════════════════════════╝
## Development

Create a virtual environment:

```bash
python3.10 -m venv .venv
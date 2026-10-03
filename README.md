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

Version: 0.5.0

Lifecycle: Day 05 / 50

2. Motive of the day

Build a centralized observability foundation that provides:

Consistent logging: one configuration point controlled by the validated MAURYA_LOG_LEVEL setting.

Request traceability: a unique request ID for each request, with support for valid UUIDs supplied by trusted clients or upstream infrastructure.

Response correlation: return the request ID in the X-Request-ID response header.

Safe diagnostics: avoid logging API keys, request bodies, or other sensitive payloads.

Testability: verify logging configuration and request-ID behavior with automated tests.

Architectural continuity: retain the Day 03 application lifecycle, database session dependency, and Day 04 settings model.

The intended outcome is a foundation that will help diagnose future failures across API handling, persistence, and asynchronous intelligence collection.
## Development

Create a virtual environment:

```bash
python3.10 -m venv .venv
```
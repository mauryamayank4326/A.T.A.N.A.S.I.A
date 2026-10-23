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

Version: 0.8.0

Lifecycle: Day 08 / 50

Day 08 extends M.A.U.R.Y.A.'s relational schema with discovered-email persistence and strengthens scan-level provenance for reconnaissance findings.

The intended schema now represents targets, scan executions, subdomains, exposed ports, and discovered email addresses. All findings remain associated with their originating scan, providing a foundation for later collection and analysis services.
## Development

Create a virtual environment:

```bash
python3.10 -m venv .venv
```

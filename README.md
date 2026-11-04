# agq-probe

A synthetic probe job for testing AGQ as an overflow backend (grid 71ec4ccc, 2026-11-03). Python stdlib only, no network, no data.

Run: `python3 run_probe.py` (image: any Python 3.9+, for example `python:3.12-slim`). It writes `out/junit.xml` and `out/evidence.json`, and ends with `ovf-evidence: result=... sha=... tests=5 failures=0 rc=0`.

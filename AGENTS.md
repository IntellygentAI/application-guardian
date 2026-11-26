# Agents working in this repository

This file is for an agent editing Application Guardian itself. The audit instructions for other applications are in [SKILL.md](SKILL.md).

## Rules

- Keep `SKILL.md` under 500 lines. Add detail to `references/`.
- Do not remove an existing scenario from the original specification. Extend a reference or add a new one.
- Quick Scan, Full Audit, and Release Gate stay read-only in the instructions.
- Do not invent benchmark numbers, download counts, or agent compatibility. [docs/benchmarks.md](docs/benchmarks.md) and [docs/compatibility.md](docs/compatibility.md) say what is unmeasured or unverified.
- Do not add a dependency to the scripts. Use the Python standard library.
- Do not overwrite existing audit files in `scaffold_audit.py`.
- Do not push, publish a release, or change repository settings unless the user asks.

## Before you finish

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

Run the release gate on a GO document and a NO-GO document. The tests already do this. If you change the decision rules, update the tests and [references/verification-protocol.md](references/verification-protocol.md) together.

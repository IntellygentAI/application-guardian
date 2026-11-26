#!/usr/bin/env python3
"""Scaffold Application Guardian audit files in a target repository.

Usage:
    python scripts/scaffold_audit.py
    python scripts/scaffold_audit.py --out path/to/docs/audits
    python scripts/scaffold_audit.py --verify
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
REQUIRED = (
    "SKILL.md",
    "references/functional-testing.md",
    "references/security-testing.md",
    "references/data-privacy.md",
    "references/database-security.md",
    "references/api-security.md",
    "references/payment-security.md",
    "references/ai-security.md",
    "references/accessibility.md",
    "references/production-readiness.md",
    "templates/audit-report.md",
    "templates/threat-model.md",
    "templates/test-matrix.md",
    "templates/release-checklist.md",
    "scripts/scaffold_audit.py",
)

COPIES = {
    "audit-report.md": "application-audit.md",
    "threat-model.md": "threat-model.md",
    "test-matrix.md": "test-matrix.md",
    "release-checklist.md": "production-readiness.md",
}

FINDINGS = """# Security findings

| ID | Title | Severity | Confidence | Verification |
| --- | --- | --- | --- | --- |

Record every finding with the schema in `templates/audit-report.md`. Do not paste secrets or private customer data.
"""

REMEDIATION = """# Remediation plan

Fix critical and high findings first. Each row needs a regression test and evidence before it is marked verified.

| Finding | Change | Regression test | Verification | Deployment note |
| --- | --- | --- | --- | --- |
"""


def verify() -> int:
    missing = [rel for rel in REQUIRED if not (ROOT / rel).is_file()]
    if missing:
        print("Missing skill files:", file=sys.stderr)
        for rel in missing:
            print(f"  {rel}", file=sys.stderr)
        return 1
    print(f"Skill structure OK ({len(REQUIRED)} files) at {ROOT}")
    return 0


def scaffold(out: Path) -> int:
    if not TEMPLATES.is_dir():
        print(f"Templates not found: {TEMPLATES}", file=sys.stderr)
        return 1
    out.mkdir(parents=True, exist_ok=True)
    for source_name, dest_name in COPIES.items():
        dest = out / dest_name
        if dest.exists():
            print(f"Keep existing {dest}")
            continue
        dest.write_text((TEMPLATES / source_name).read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Wrote {dest}")
    for name, body in (("security-findings.md", FINDINGS), ("remediation-plan.md", REMEDIATION)):
        dest = out / name
        if dest.exists():
            print(f"Keep existing {dest}")
            continue
        dest.write_text(body, encoding="utf-8")
        print(f"Wrote {dest}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold or verify Application Guardian files.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/audits"),
        help="Directory for audit artefacts (default: docs/audits)",
    )
    parser.add_argument("--verify", action="store_true", help="Check this skill's required files.")
    args = parser.parse_args()
    if args.verify:
        return verify()
    return scaffold(args.out)


if __name__ == "__main__":
    raise SystemExit(main())

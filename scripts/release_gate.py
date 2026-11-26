#!/usr/bin/env python3
"""Calculate a release decision from structured audit evidence.

Exit 0 for GO and CONDITIONAL GO.
Exit 1 for NO-GO.
Exit 2 when the document is not valid.
Pass --strict to treat CONDITIONAL GO as exit 1.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from guardianlib import decide
from validate_report import validate_audit


def evaluate(document: dict, strict: bool) -> int:
    errors = validate_audit(document)
    if errors:
        print("Audit document is invalid:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 2
    result = decide(document)
    decision = result["release_decision"]
    print(decision)
    for reason in result["reasons"]:
        print(f"- {reason}")
    if not result["reasons"] and decision == "GO":
        print("- Mandatory checks passed and no unresolved release-blocking finding remains.")
    if decision == "CONDITIONAL GO":
        print("- Lower-severity risks are accepted. GO is not claimed.")
    if decision == "NO-GO":
        return 1
    if strict and decision == "CONDITIONAL GO":
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate an Application Guardian audit result.")
    parser.add_argument("audit_json", type=Path, help="Path to audit-result.json")
    parser.add_argument(
        "--head",
        help="Current Git commit. Defaults to HEAD of the repository that contains the audit file. "
        "Exit 2 when neither is available.",
    )
    parser.add_argument("--strict", action="store_true", help="Exit 1 for CONDITIONAL GO as well as NO-GO.")
    args = parser.parse_args()
    if not args.audit_json.is_file():
        print(f"Audit file not found: {args.audit_json}", file=sys.stderr)
        return 2
    try:
        document = json.loads(args.audit_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Audit file is not JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(document, dict):
        print("Audit file must contain a JSON object.", file=sys.stderr)
        return 2
    head = args.head or current_commit(args.audit_json.resolve().parent)
    if not head:
        print(
            "Cannot read the current commit. Pass --head, or run inside the application's Git repository.",
            file=sys.stderr,
        )
        return 2
    # The real HEAD always replaces any head_commit written into the file,
    # so a report cannot vouch for its own freshness.
    document["head_commit"] = head
    return evaluate(document, args.strict)


def current_commit(directory: Path) -> str:
    """Return HEAD of the Git repository that contains the audit file, or ''."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return completed.stdout.strip() if completed.returncode == 0 else ""


if __name__ == "__main__":
    raise SystemExit(main())

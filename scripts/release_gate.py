#!/usr/bin/env python3
"""Calculate a release decision from structured audit evidence.

Exit 0 for GO and CONDITIONAL GO.
Exit 1 for NO-GO.
Exit 2 when the document is not valid or the current commit cannot be read.
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


def evaluate(document: dict, strict: bool, worktree_changes: list[str] | None = None) -> int:
    errors = validate_audit(document)
    if errors:
        print("Audit document is invalid:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 2
    result = decide(document, worktree_changes=worktree_changes)
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
    audit_path = args.audit_json.resolve()
    head = args.head or current_commit(audit_path.parent)
    if not head:
        print(
            "Cannot read the current commit. Pass --head, or run inside the application's Git repository.",
            file=sys.stderr,
        )
        return 2
    # The real HEAD always replaces any head_commit written into the file,
    # so a report cannot vouch for its own freshness.
    document["head_commit"] = head
    return evaluate(document, args.strict, uncommitted_changes(audit_path))


def git(directory: Path, *arguments: str) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(
            ["git", "-C", str(directory), *arguments],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def current_commit(directory: Path) -> str:
    """Return HEAD of the Git repository that contains the audit file, or ''."""
    completed = git(directory, "rev-parse", "HEAD")
    return completed.stdout.strip() if completed and completed.returncode == 0 else ""


def uncommitted_changes(audit_path: Path) -> list[str]:
    """Return changed or untracked paths outside the audit folder.

    Evidence describes a commit. Code that is modified but not committed was
    not what the checks ran against. The audit folder itself is ignored, since
    the report is written there. When the audit file sits at the repository
    root, only the audit file is ignored. Outside a Git repository, nothing can
    be checked and the list is empty.
    """
    top = git(audit_path.parent, "rev-parse", "--show-toplevel")
    if not top or top.returncode != 0:
        return []
    root = Path(top.stdout.strip()).resolve()
    status = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if not status or status.returncode != 0:
        return []
    relative_file = audit_path.relative_to(root).as_posix()
    audit_dir = audit_path.parent.relative_to(root).as_posix()
    changed: list[str] = []
    entries = status.stdout.split("\0")
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if len(entry) < 4:
            continue
        code, path = entry[:2], entry[3:]
        if code[0] in "RC":
            index += 1  # the next entry is the rename source
        if path == relative_file:
            continue
        if audit_dir not in {"", "."} and (path == audit_dir or path.startswith(audit_dir + "/")):
            continue
        changed.append(path)
    return changed


if __name__ == "__main__":
    raise SystemExit(main())

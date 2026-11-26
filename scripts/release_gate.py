#!/usr/bin/env python3
"""Calculate a release decision from structured audit evidence.

Exit 0 for GO and CONDITIONAL GO.
Exit 1 for NO-GO.
Exit 2 when the document is not valid or the current commit cannot be read.
Pass --strict to treat CONDITIONAL GO as exit 1.
Pass --ci-evidence with the file written by ci_evidence.py to require that CI
repeated every recorded run on this commit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from guardianlib import decide
from validate_report import validate_audit


def evaluate(
    document: dict,
    strict: bool,
    worktree_changes: list[str] | None = None,
    worktree_verified: bool = True,
    equivalent_commits: set[str] | None = None,
    ci_evidence: dict | None = None,
    ci_expected: dict[str, str] | None = None,
) -> int:
    errors = validate_audit(document)
    if errors:
        print("Audit document is invalid:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 2
    result = decide(
        document,
        worktree_changes=worktree_changes,
        worktree_verified=worktree_verified,
        equivalent_commits=equivalent_commits,
        ci_evidence=ci_evidence,
        ci_expected=ci_expected,
    )
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
    parser.add_argument(
        "--ci-evidence",
        type=Path,
        help="Evidence file from ci_evidence.py. Every runtime PASS must have a passing CI run of its command.",
    )
    args = parser.parse_args()
    if not args.audit_json.is_file():
        print(f"Audit file not found: {args.audit_json}", file=sys.stderr)
        return 2
    raw = args.audit_json.read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
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
    ci_evidence = None
    ci_expected = None
    if args.ci_evidence is not None:
        try:
            ci_evidence = json.loads(args.ci_evidence.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"CI evidence cannot be read: {exc}", file=sys.stderr)
            return 2
        ci_expected = {
            "audit_sha256": hashlib.sha256(raw).hexdigest(),
            "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        }
    changes = uncommitted_changes(audit_path)
    return evaluate(
        document,
        args.strict,
        changes,
        worktree_verified=changes is not None,
        equivalent_commits=equivalent_commits(audit_path, head, document),
        ci_evidence=ci_evidence,
        ci_expected=ci_expected,
    )


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


# The files an audit writes. Only these, and the audit file itself, may change
# without a new commit. Anything else in the same folder still counts.
REPORT_FILES = frozenset(
    {
        "application-audit.md",
        "security-findings.md",
        "threat-model.md",
        "test-matrix.md",
        "remediation-plan.md",
        "production-readiness.md",
        "audit-result.json",
    }
)


COMMIT_ID = re.compile(r"[0-9a-f]{7,64}")


def _is_report(path: str, relative_file: str, audit_dir: str) -> bool:
    if path == relative_file:
        return True
    folder, _, name = path.rpartition("/")
    return folder == audit_dir and name in REPORT_FILES


def _audit_location(audit_path: Path) -> tuple[Path, str, str] | None:
    """Return the repository root, the audit file, and its folder, relative to the root."""
    top = git(audit_path.parent, "rev-parse", "--show-toplevel")
    if not top or top.returncode != 0:
        return None
    root = Path(top.stdout.strip()).resolve()
    try:
        relative_file = audit_path.relative_to(root).as_posix()
    except ValueError:
        return None
    audit_dir = audit_path.parent.relative_to(root).as_posix()
    return root, relative_file, "" if audit_dir == "." else audit_dir


def equivalent_commits(audit_path: Path, head: str, document: dict) -> set[str]:
    """Return recorded commits whose code is identical to head.

    Committing the audit reports creates a new commit. Evidence recorded on
    the commit before it is still current when the only files that changed
    since are the audit file and its report files, and that commit is an
    ancestor of head. Anything else, including a commit Git cannot find,
    stays stale. A recorded commit must be a hexadecimal commit ID: a name
    such as HEAD or main would always resolve to the current code.
    """
    location = _audit_location(audit_path)
    if location is None:
        return set()
    root, relative_file, audit_dir = location
    recorded = {str(document.get("commit") or "").strip()}
    for item in [*(document.get("mandatory_checks") or []), *(document.get("findings") or [])]:
        if isinstance(item, dict):
            recorded.add(str(item.get("commit") or "").strip())
    recorded.discard("")
    recorded.discard(head)
    same: set[str] = set()
    for commit in recorded:
        if not COMMIT_ID.fullmatch(commit):
            continue
        ancestor = git(root, "merge-base", "--is-ancestor", f"{commit}^{{commit}}", head)
        if not ancestor or ancestor.returncode != 0:
            continue
        diff = git(root, "diff", "--name-only", "--no-renames", "-z", commit, head, "--")
        if not diff or diff.returncode != 0:
            continue
        paths = [path for path in diff.stdout.split("\0") if path]
        if all(_is_report(path, relative_file, audit_dir) for path in paths):
            same.add(commit)
    return same


def uncommitted_changes(audit_path: Path) -> list[str] | None:
    """Return changed or untracked paths that are not audit reports.

    Evidence describes a commit. Code that is modified but not committed was
    not what the checks ran against. The audit file and the report files next
    to it are ignored, since the audit writes them. Every other path counts,
    including other files in the audit folder.

    Returns None when the working tree cannot be checked: the audit file is
    not inside a Git repository, or git status fails. The gate treats that as
    NO-GO, never as a clean tree.
    """
    location = _audit_location(audit_path)
    if location is None:
        return None
    root, relative_file, audit_dir = location
    status = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if not status or status.returncode != 0:
        return None
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
        if _is_report(path, relative_file, audit_dir):
            continue
        changed.append(path)
    return changed


if __name__ == "__main__":
    raise SystemExit(main())

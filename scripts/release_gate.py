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

from guardian_controls import load_registry, registry_file_problems
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
    extra_runners: frozenset[str] | set[str] = frozenset(),
    extra_reasons: list[str] | None = None,
    controls: dict | None = None,
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
        extra_runners=extra_runners,
        extra_reasons=extra_reasons,
        controls=controls,
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
    parser.add_argument(
        "--allow-runner",
        action="append",
        default=[],
        help="Accept another test runner name in critical check commands. Pass it to ci_evidence.py with --allow too.",
    )
    parser.add_argument(
        "--controls",
        type=Path,
        help="Control registry (guardian-checks.json). Each critical PASS must use its registry command; "
        "with --ci-evidence, every required test must have run and passed in the test report.",
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
    actual = current_commit(audit_path.parent)
    head = args.head or actual
    extra_reasons = []
    if args.head and actual and not actual.startswith(args.head):
        extra_reasons.append(
            f"--head {args.head} is not the repository's HEAD ({actual}). The gate decides for the commit that is checked out."
        )
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
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
            "repository": os.environ.get("GITHUB_REPOSITORY", ""),
        }
    controls = None
    if args.controls is not None:
        controls, problems = load_registry(args.controls)
        location = _audit_location(audit_path)
        if location is None:
            problems.append("The control registry cannot be checked outside a Git repository.")
        else:
            problems.extend(registry_file_problems(location[0], args.controls, controls))
        extra_reasons.extend(problems)
    changes = uncommitted_changes(audit_path)
    return evaluate(
        document,
        args.strict,
        changes,
        worktree_verified=changes is not None,
        equivalent_commits=equivalent_commits(audit_path, head, document),
        ci_evidence=ci_evidence,
        ci_expected=ci_expected,
        extra_runners=frozenset(args.allow_runner),
        extra_reasons=extra_reasons,
        controls=controls,
    )


def git(directory: Path, *arguments: str) -> subprocess.CompletedProcess | None:
    """Run git and decode its output, keeping any byte that is not valid UTF-8."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(directory), *arguments],
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    completed.stdout = completed.stdout.decode("utf-8", "surrogateescape")
    completed.stderr = completed.stderr.decode("utf-8", "surrogateescape")
    return completed


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


def _shown(path: str) -> str:
    """A path as text that can always be printed, with bad bytes escaped."""
    return path.encode("utf-8", "surrogateescape").decode("utf-8", "backslashreplace")


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
        # The ID must name that commit: a tag called "deadbee" resolves to a
        # different commit, whose ID does not start with "deadbee".
        resolved = git(root, "rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}")
        if not resolved or resolved.returncode != 0 or not resolved.stdout.strip().startswith(commit):
            continue
        full = resolved.stdout.strip()
        ancestor = git(root, "merge-base", "--is-ancestor", full, head)
        if not ancestor or ancestor.returncode != 0:
            continue
        diff = git(root, "diff", "--name-only", "--no-renames", "--ignore-submodules=none", "-z", full, head, "--")
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
    status = git(
        root, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--no-renames", "--ignore-submodules=none"
    )
    if not status or status.returncode != 0:
        return None
    changed: list[str] = []
    # Without rename detection, a file moved to a report name shows as a
    # deletion and an addition, so the deleted code still counts.
    for entry in status.stdout.split("\0"):
        if len(entry) < 4:
            continue
        path = entry[3:]
        if not _is_report(path, relative_file, audit_dir):
            changed.append(_shown(path))
    # Files marked skip-worktree or assume-unchanged are hidden from git status.
    flags = git(root, "ls-files", "-v", "-z")
    if not flags or flags.returncode != 0:
        return None
    for entry in flags.stdout.split("\0"):
        if len(entry) > 2 and (entry[0] == "S" or entry[0].islower()):
            changed.append(f"{_shown(entry[2:])} (hidden from git status by skip-worktree or assume-unchanged)")
    return changed


if __name__ == "__main__":
    raise SystemExit(main())

"""Release-decision rules shared by the CLI and the tests.

The decision is calculated from structured evidence. Prose in a Markdown
report does not override this result.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BLOCKING_SEVERITIES = {"critical", "high"}
ACCEPTABLE_SEVERITIES = {"medium", "low"}
OPEN_STATUSES = {"open", "suspected", "unresolved"}
CLOSED_STATUSES = {"fixed", "false_positive", "accepted"}
PASSING_CHECKS = {"PASS", "NOT APPLICABLE"}
RUNTIME_REQUIRED = {"static", "none", ""}

GO = "GO"
CONDITIONAL = "CONDITIONAL GO"
NO_GO = "NO-GO"

INVENTORY_PATH = Path(__file__).resolve().parent.parent / "schemas" / "mandatory-checks.json"


def load_inventory(path: Path = INVENTORY_PATH) -> list[dict[str, Any]]:
    """Return the mandatory checks every audit result must contain."""
    return json.loads(path.read_text(encoding="utf-8"))["checks"]


def _text(item: dict[str, Any], key: str) -> str:
    return str(item.get(key) or "").strip()


def _missing_execution(item: dict[str, Any], reference: str) -> list[str]:
    """Name what an executed, passing run on the reference commit still lacks."""
    missing = []
    if _text(item, "commit") != reference:
        missing.append(f"commit {reference}")
    if not _text(item, "command"):
        missing.append("command")
    if item.get("exit_code") != 0:
        missing.append("exit code 0")
    if not _text(item, "observed"):
        missing.append("observed result")
    if not _text(item, "executed_at"):
        missing.append("timestamp")
    return missing


def decide(
    document: dict[str, Any],
    inventory: list[dict[str, Any]] | None = None,
    worktree_changes: list[str] | None = None,
    worktree_verified: bool = True,
) -> dict[str, Any]:
    """Return a decision, the reasons, and whether release is allowed.

    inventory defaults to schemas/mandatory-checks.json. worktree_changes are
    paths with uncommitted changes that are not audit reports; the CLI fills
    it. worktree_verified is False when the CLI could not run git status, and
    the decision is then NO-GO.
    """
    reasons: list[str] = []
    findings = document.get("findings") or []
    checks = document.get("mandatory_checks") or []
    inventory = load_inventory() if inventory is None else inventory

    audited = _text(document, "commit")
    head = _text(document, "head_commit")
    if audited and head and audited != head:
        reasons.append(f"Evidence was recorded at {audited} and HEAD is {head}. The evidence is stale.")

    # The commit the release is for. Evidence from any other commit is stale.
    reference = head or audited

    if not worktree_verified:
        reasons.append(
            "Could not confirm that the working tree matches the commit: the audit file is not "
            "inside a Git repository, or git status failed. Run the gate inside the application's repository."
        )

    if worktree_changes:
        shown = ", ".join(worktree_changes[:5])
        more = f" and {len(worktree_changes) - 5} more" if len(worktree_changes) > 5 else ""
        reasons.append(
            f"The working tree has uncommitted changes that were not audited: {shown}{more}. "
            "Commit them and re-run the checks."
        )

    # Accepted risks need an owner and an approval record.
    risks: dict[str, dict[str, Any]] = {}
    for risk in document.get("accepted_risks") or []:
        if not isinstance(risk, dict):
            reasons.append(f"Accepted risk {risk!r} has no owner or approval record.")
            continue
        risk_id = _text(risk, "id")
        missing = [key for key in ("owner", "approved_by", "approved_at", "reason") if not _text(risk, key)]
        if missing:
            reasons.append(f"Accepted risk {risk_id or 'unknown'} is missing {', '.join(missing)}.")
            continue
        risks[risk_id] = risk

    accepted_lower: list[str] = []
    for finding in findings:
        severity = _text(finding, "severity").lower()
        status = _text(finding, "status").lower()
        finding_id = _text(finding, "id") or "unknown"
        if status == "fixed" and severity in BLOCKING_SEVERITIES:
            evidence = _text(finding, "evidence_type") or "none"
            if evidence in RUNTIME_REQUIRED:
                reasons.append(
                    f"{finding_id} is a {severity} finding marked fixed with {evidence} evidence. "
                    "A fix is verified only by an executed test."
                )
                continue
            missing = _missing_execution(finding, reference)
            if missing:
                reasons.append(
                    f"{finding_id} is a {severity} finding marked fixed, but its verification lacks "
                    f"{', '.join(missing)}."
                )
            continue
        if status in {"fixed", "false_positive"}:
            continue
        if severity in BLOCKING_SEVERITIES and status == "accepted":
            reasons.append(
                f"{finding_id} is {severity} and cannot be accepted. Resolve it or the decision stays NO-GO."
            )
            continue
        if severity in BLOCKING_SEVERITIES and status in OPEN_STATUSES:
            reasons.append(f"{finding_id} is an unresolved {severity} finding.")
            continue
        if severity in ACCEPTABLE_SEVERITIES and status == "accepted":
            if finding_id in risks:
                accepted_lower.append(finding_id)
            else:
                reasons.append(f"{finding_id} is marked accepted but has no approved entry in accepted_risks.")
            continue
        if severity in ACCEPTABLE_SEVERITIES and status in OPEN_STATUSES:
            reasons.append(f"{finding_id} is an open {severity} finding and has no explicit acceptance.")

    accepted_ids = {_text(f, "id") for f in findings if _text(f, "status").lower() == "accepted"}
    for risk_id in sorted(set(risks) - accepted_ids):
        reasons.append(f"Accepted risk {risk_id} does not match an accepted finding.")

    if not checks:
        reasons.append("No mandatory checks were recorded.")

    # Every mandatory check is present once, with its critical flag intact.
    seen: dict[str, int] = {}
    for check in checks:
        check_id = _text(check, "id")
        seen[check_id] = seen.get(check_id, 0) + 1
    for check_id, count in sorted(seen.items()):
        if count > 1:
            reasons.append(f"Check {check_id} appears {count} times. Each check id must be unique.")
    by_id = {_text(check, "id"): check for check in checks}
    missing_ids = [item["id"] for item in inventory if item["id"] not in by_id]
    if missing_ids:
        reasons.append(
            f"{len(missing_ids)} mandatory check(s) are missing from the audit: {', '.join(missing_ids)}."
        )
    required_critical = {item["id"] for item in inventory if item.get("critical")}

    passed = 0
    for check in checks:
        status = _text(check, "status")
        check_id = _text(check, "id") or "unknown"
        critical = bool(check.get("critical")) or check_id in required_critical
        if check_id in required_critical and not check.get("critical"):
            reasons.append(f"{check_id} is a critical check and cannot be recorded as non-critical.")
        evidence = _text(check, "evidence_type") or "none"
        if status == "PASS":
            check_commit = _text(check, "commit")
            if not check_commit:
                reasons.append(
                    f"{check_id} passed with no recorded commit. Evidence that cannot be tied to a commit is not fresh."
                )
                continue
            if reference and check_commit != reference:
                reasons.append(f"{check_id} passed at {check_commit}, not at {reference}. The evidence is stale.")
                continue
            if critical and evidence in RUNTIME_REQUIRED:
                reasons.append(
                    f"{check_id} is a critical control with {evidence} evidence. Runtime evidence is required."
                )
                continue
            if evidence == "runtime":
                missing = _missing_execution(check, reference)
                if missing:
                    reasons.append(f"{check_id} passed without a recorded run: missing {', '.join(missing)}.")
                    continue
            elif not _text(check, "observed"):
                reasons.append(f"{check_id} passed on static evidence but does not say what was observed.")
                continue
            passed += 1
            continue
        if status == "NOT APPLICABLE":
            if not _text(check, "justification"):
                reasons.append(f"{check_id} is NOT APPLICABLE without a justification.")
            continue
        if status == "FAIL":
            reasons.append(f"{check_id} failed.")
            continue
        reasons.append(f"{check_id} is {status or 'missing'}. An unverified mandatory check blocks release.")

    if checks and passed == 0:
        reasons.append("No mandatory check has a PASS result.")

    if reasons:
        decision = NO_GO
    elif accepted_lower:
        decision = CONDITIONAL
    else:
        decision = GO

    return {
        "release_decision": decision,
        "reasons": reasons,
        "release_allowed": decision in {GO, CONDITIONAL},
        "passed_checks": passed,
    }

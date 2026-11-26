"""Release-decision rules shared by the CLI and the tests.

The decision is calculated from structured evidence. Prose in a Markdown
report does not override this result.
"""

from __future__ import annotations

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


def decide(document: dict[str, Any]) -> dict[str, Any]:
    """Return a decision, the reasons, and whether release is allowed."""
    reasons: list[str] = []
    findings = document.get("findings") or []
    checks = document.get("mandatory_checks") or []
    accepted = set(document.get("accepted_risks") or [])

    audited = str(document.get("commit") or "")
    head = str(document.get("head_commit") or "")
    if audited and head and audited != head:
        reasons.append(
            f"Evidence was recorded at {audited} and HEAD is {head}. The evidence is stale."
        )

    # The commit the release is for. Evidence from any other commit is stale.
    reference = head or audited

    for finding in findings:
        severity = str(finding.get("severity") or "").lower()
        status = str(finding.get("status") or "").lower()
        finding_id = str(finding.get("id") or "unknown")
        if status == "fixed" and severity in BLOCKING_SEVERITIES:
            evidence = str(finding.get("evidence_type") or "none")
            if evidence in RUNTIME_REQUIRED:
                reasons.append(
                    f"{finding_id} is a {severity} finding marked fixed with {evidence} evidence. "
                    "A fix is verified only by an executed test."
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
            if finding_id not in accepted:
                reasons.append(
                    f"{finding_id} is marked accepted but is missing from accepted_risks."
                )
            continue
        if severity in ACCEPTABLE_SEVERITIES and status in OPEN_STATUSES:
            reasons.append(
                f"{finding_id} is an open {severity} finding and has no explicit acceptance."
            )

    if not checks:
        reasons.append("No mandatory checks were recorded.")

    passed = 0
    for check in checks:
        status = str(check.get("status") or "")
        check_id = str(check.get("id") or "unknown")
        critical = bool(check.get("critical"))
        evidence = str(check.get("evidence_type") or "none")
        check_commit = str(check.get("commit") or "")
        if status == "PASS" and check_commit and reference and check_commit != reference:
            reasons.append(
                f"{check_id} passed at {check_commit}, not at {reference}. The evidence is stale."
            )
            continue
        if status == "PASS":
            passed += 1
            if critical and evidence in RUNTIME_REQUIRED:
                reasons.append(
                    f"{check_id} is a critical control with {evidence or 'no'} evidence. Runtime evidence is required."
                )
            continue
        if status == "NOT APPLICABLE":
            continue
        if status == "FAIL":
            reasons.append(f"{check_id} failed.")
            continue
        reasons.append(f"{check_id} is {status or 'missing'}. An unverified mandatory check blocks release.")

    if checks and passed == 0:
        reasons.append("No mandatory check has a PASS result.")

    blocking = [reason for reason in reasons if reason]
    accepted_lower = [
        finding
        for finding in findings
        if str(finding.get("severity") or "").lower() in ACCEPTABLE_SEVERITIES
        and str(finding.get("status") or "").lower() == "accepted"
        and str(finding.get("id") or "") in accepted
    ]

    if blocking:
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

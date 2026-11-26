"""Release-decision rules shared by the CLI and the tests.

The decision is calculated from structured evidence. Prose in a Markdown
report does not override this result.
"""

from __future__ import annotations

import json
import shlex
from datetime import datetime, timezone
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

# Programs that run tests. A critical check or a fixed critical or high finding
# must name one of these as its command, so "true" or "echo passed" cannot
# stand in for a test. ci_evidence.py refuses anything else in CI.
TEST_RUNNERS = frozenset(
    {
        "bun", "bundle", "cargo", "deno", "dotnet", "go", "gradle", "gradlew", "jest", "make", "mvn",
        "node", "npm", "npx", "php", "phpunit", "playwright", "pnpm", "pytest", "python", "python3",
        "rake", "rspec", "vitest", "yarn",
    }
)


# Flags that make a runner execute code given on the command line instead of
# a test file, so "python -c pass" cannot prove a control.
INLINE_CODE = {
    "python": {"-c"},
    "python3": {"-c"},
    "node": {"-e", "--eval", "-p", "--print"},
    "bun": {"-e", "--eval"},
    "deno": {"eval"},
    "npx": {"-c", "--call"},
}


def test_command_problem(command: str, runners: frozenset[str] | set[str]) -> str:
    """Return why a command cannot prove a control, or '' when it can."""
    name = runner_name(command)
    if name not in runners:
        return "is not a test runner"
    try:
        argv = shlex.split(command)
    except ValueError:
        return "cannot be parsed"
    if INLINE_CODE.get(name, set()) & set(argv[1:]):
        return "runs inline code instead of a test file"
    return ""


def runner_name(command: str) -> str:
    """Return the program a command starts, without its path or a Windows suffix."""
    try:
        argv = shlex.split(command)
    except ValueError:
        return ""
    if not argv:
        return ""
    name = Path(argv[0]).name
    for suffix in (".exe", ".cmd", ".bat"):
        if name.lower().endswith(suffix):
            name = name[: -len(suffix)]
    return name


def load_inventory(path: Path = INVENTORY_PATH) -> list[dict[str, Any]]:
    """Return the mandatory checks every audit result must contain."""
    return json.loads(path.read_text(encoding="utf-8"))["checks"]


def _text(item: dict[str, Any], key: str) -> str:
    return str(item.get(key) or "").strip()


def _missing_execution(item: dict[str, Any], reference: str, current: set[str] | None = None) -> list[str]:
    """Name what an executed, passing run on the reference commit still lacks."""
    missing = []
    current = current or {reference}
    if _text(item, "commit") not in current:
        missing.append(f"commit {reference}")
    if not _text(item, "command"):
        missing.append("command")
    if type(item.get("exit_code")) is not int or item.get("exit_code") != 0:
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
    equivalent_commits: set[str] | None = None,
    ci_evidence: dict[str, Any] | None = None,
    ci_expected: dict[str, str] | None = None,
    extra_runners: frozenset[str] | set[str] = frozenset(),
    extra_reasons: list[str] | None = None,
) -> dict[str, Any]:
    """Return a decision, the reasons, and whether release is allowed.

    inventory defaults to schemas/mandatory-checks.json. worktree_changes are
    paths with uncommitted changes that are not audit reports; the CLI fills
    it. worktree_verified is False when the CLI could not run git status, and
    the decision is then NO-GO. equivalent_commits are earlier commits whose
    code is identical to HEAD: only audit reports changed since. Evidence
    recorded on them is current. ci_evidence is the file written by
    ci_evidence.py; when given, every runtime PASS and every fixed critical or
    high finding needs a matching passing run in it. ci_expected holds the
    values the evidence must match: audit_sha256, run_id, run_attempt, and
    repository. extra_runners adds programs to TEST_RUNNERS.
    """
    runners = TEST_RUNNERS | set(extra_runners)
    reasons: list[str] = list(extra_reasons or [])
    findings = document.get("findings") or []
    checks = document.get("mandatory_checks") or []
    inventory = load_inventory() if inventory is None else inventory

    audited = _text(document, "commit")
    head = _text(document, "head_commit")
    equivalent = set(equivalent_commits or ())
    if audited and head and audited != head and audited not in equivalent:
        reasons.append(f"Evidence was recorded at {audited} and HEAD is {head}. The evidence is stale.")

    # The commit the release is for. Evidence from any other commit is stale,
    # unless only audit reports changed between that commit and this one.
    reference = head or audited
    current = {reference} | equivalent

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
            missing = _missing_execution(finding, reference, current)
            if missing:
                reasons.append(
                    f"{finding_id} is a {severity} finding marked fixed, but its verification lacks "
                    f"{', '.join(missing)}."
                )
            elif problem := test_command_problem(_text(finding, "command"), runners):
                reasons.append(
                    f"{finding_id} is a {severity} finding marked fixed by the command "
                    f"'{_text(finding, 'command')}', which {problem}."
                )
            continue
        if status == "false_positive" and severity in BLOCKING_SEVERITIES and not _text(finding, "challenge"):
            reasons.append(
                f"{finding_id} is a {severity} finding closed as a false positive without a recorded challenge. "
                "Say which guard stops it and how that was tested."
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
    critical_tested = 0
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
            if reference and check_commit not in current:
                reasons.append(f"{check_id} passed at {check_commit}, not at {reference}. The evidence is stale.")
                continue
            if critical and evidence in RUNTIME_REQUIRED:
                reasons.append(
                    f"{check_id} is a critical control with {evidence} evidence. Runtime evidence is required."
                )
                continue
            if evidence == "runtime":
                missing = _missing_execution(check, reference, current)
                if missing:
                    reasons.append(f"{check_id} passed without a recorded run: missing {', '.join(missing)}.")
                    continue
                problem = test_command_problem(_text(check, "command"), runners)
                if critical and problem:
                    reasons.append(
                        f"{check_id} is a critical check that passed with the command '{_text(check, 'command')}', "
                        f"which {problem}."
                    )
                    continue
                if critical:
                    critical_tested += 1
            elif not _text(check, "observed"):
                reasons.append(f"{check_id} passed on static evidence but does not say what was observed.")
                continue
            passed += 1
            continue
        if status == "NOT APPLICABLE":
            if not _text(check, "justification"):
                reasons.append(f"{check_id} is NOT APPLICABLE without a justification.")
            elif critical and not _text(check, "approved_by"):
                reasons.append(
                    f"{check_id} is a critical check marked NOT APPLICABLE without approved_by. "
                    "A named reviewer must confirm that the control does not apply."
                )
            continue
        if status == "FAIL":
            reasons.append(f"{check_id} failed.")
            continue
        reasons.append(f"{check_id} is {status or 'missing'}. An unverified mandatory check blocks release.")

    if checks and passed == 0:
        reasons.append("No mandatory check has a PASS result.")
    elif checks and critical_tested == 0:
        reasons.append(
            "No critical check passed with an executed test. Every application has at least one critical "
            "control that applies, such as authentication or secrets."
        )

    today = datetime.now(timezone.utc).date().isoformat()
    for risk_id, risk in sorted(risks.items()):
        expires = _text(risk, "expires_at")
        if expires and expires[:10] < today:
            reasons.append(f"Accepted risk {risk_id} expired on {expires[:10]}. Review it again or fix it.")

    if ci_evidence is not None:
        reasons.extend(ci_reasons(document, ci_evidence, reference, ci_expected or {}))

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


CI_SCHEMA_VERSION = "1.0"


def recorded_runs(document: dict[str, Any]) -> list[tuple[str, str]]:
    """Return (id, command) for every run that CI must repeat.

    These are runtime PASS checks and fixed critical or high findings: the
    places where the gate trusts an executed command.
    """
    runs = []
    for check in document.get("mandatory_checks") or []:
        if _text(check, "status") == "PASS" and _text(check, "evidence_type") == "runtime":
            runs.append((_text(check, "id"), _text(check, "command")))
    for finding in document.get("findings") or []:
        if (
            _text(finding, "status").lower() == "fixed"
            and _text(finding, "severity").lower() in BLOCKING_SEVERITIES
        ):
            runs.append((_text(finding, "id"), _text(finding, "command")))
    return runs


def ci_reasons(
    document: dict[str, Any], evidence: dict[str, Any], head: str, expected: dict[str, str]
) -> list[str]:
    """Compare the audit's recorded runs with what CI actually ran."""
    if not isinstance(evidence, dict) or evidence.get("schema_version") != CI_SCHEMA_VERSION:
        return [f"CI evidence is not a version {CI_SCHEMA_VERSION} evidence file."]
    reasons = []
    if not expected.get("run_id"):
        reasons.append("GITHUB_RUN_ID is not set, so the CI evidence cannot be tied to this workflow run.")
    if _text(evidence, "commit") != head:
        reasons.append(f"CI evidence was produced at {_text(evidence, 'commit') or 'no commit'}, not at {head}.")
    run_id = expected.get("run_id")
    if run_id and _text(evidence, "run_id") != run_id:
        reasons.append("CI evidence comes from a different workflow run. It must be produced in this run.")
    attempt = expected.get("run_attempt")
    if attempt and _text(evidence, "run_attempt") != attempt:
        reasons.append("CI evidence comes from a different attempt of this workflow run.")
    repository = expected.get("repository")
    if repository and _text(evidence, "repository") != repository:
        reasons.append(f"CI evidence was produced for {_text(evidence, 'repository') or 'no repository'}, not {repository}.")
    audit_hash = expected.get("audit_sha256")
    if audit_hash and _text(evidence, "audit_sha256") != audit_hash:
        reasons.append("The audit file changed after CI ran the recorded commands.")
    by_id: dict[str, dict[str, Any]] = {}
    for run in evidence.get("runs") or []:
        if isinstance(run, dict):
            for item_id in run.get("ids") or []:
                if str(item_id) in by_id:
                    reasons.append(f"{item_id} appears in more than one CI run.")
                by_id[str(item_id)] = run
    for item_id, command in recorded_runs(document):
        run = by_id.get(item_id)
        if run is None:
            reasons.append(f"{item_id}: CI has no run of its recorded command.")
        elif _text(run, "command") != command:
            reasons.append(f"{item_id}: CI ran a different command from the one recorded.")
        elif run.get("rejected"):
            reasons.append(f"{item_id}: CI refused to run the command: {_text(run, 'rejected')}.")
        elif run.get("timed_out"):
            reasons.append(f"{item_id}: the command timed out in CI.")
        elif type(run.get("exit_code")) is not int or run.get("exit_code") != 0:
            reasons.append(f"{item_id}: the command exited {run.get('exit_code')} in CI.")
    return reasons

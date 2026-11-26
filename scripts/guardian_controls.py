"""Bind mandatory checks to reviewed tests, and read native test reports.

A control registry (guardian-checks.json, committed and owned in CODEOWNERS)
says which tests prove each mandatory check. ci_evidence.py runs the recorded
command with the runner's own machine-readable report turned on, and records
the outcome of every test in it. The release gate then requires that each
required test ran and passed, so a command that exits 0 without running the
right tests is NO-GO.

Supported runners: pytest, through its JUnit XML report. Any other runner is
recorded as unverified. It never passes a controlled check on its exit code.
"""

from __future__ import annotations

import json
import shlex
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Any

REGISTRY_VERSION = "1.0"
SUPPORTED_RUNNERS = frozenset({"pytest"})
CODEOWNERS_PATHS = (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")

# Arguments that make a runner print information instead of running tests.
INFORMATION_ARGUMENTS = frozenset(
    {
        "--version", "-V", "version", "--help", "-h", "help", "--collect-only", "--co",
        "--fixtures", "--markers", "--listTests", "--list", "-list", "--showConfig",
    }
)


def information_only(argv: list[str]) -> bool:
    """True when the command asks the runner for version, help, or a test list."""
    return bool(INFORMATION_ARGUMENTS & set(argv[1:]))


def load_registry(path: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Return the controls by check ID, and the problems with the file."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, [f"The control registry {path.name} cannot be read: {exc}"]
    return load_registry_document(document)


def load_registry_document(document: Any) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Validate a parsed registry and return its controls by check ID, and its problems."""
    if not isinstance(document, dict) or document.get("schema_version") != REGISTRY_VERSION:
        return {}, [f"The control registry must be a version {REGISTRY_VERSION} object."]
    controls: dict[str, dict[str, Any]] = {}
    problems: list[str] = []
    for entry in document.get("controls") or []:
        if not isinstance(entry, dict):
            problems.append("Every control registry entry must be an object.")
            continue
        check_id = str(entry.get("check_id") or "").strip()
        tests = entry.get("required_tests")
        if not check_id:
            problems.append("A control registry entry has no check_id.")
            continue
        if check_id in controls:
            problems.append(f"Control registry lists {check_id} more than once.")
            continue
        if entry.get("runner") not in SUPPORTED_RUNNERS:
            problems.append(
                f"Control registry entry {check_id} uses runner {entry.get('runner')!r}. Only "
                f"{', '.join(sorted(SUPPORTED_RUNNERS))} reports can be verified; record the check as NOT TESTED."
            )
            continue
        if not str(entry.get("command") or "").strip():
            problems.append(f"Control registry entry {check_id} has no command.")
            continue
        if not isinstance(tests, list) or not tests or not all(isinstance(t, str) and "::" in t for t in tests):
            problems.append(
                f"Control registry entry {check_id} must list required_tests as pytest test IDs, "
                "such as tests/test_invoices.py::test_other_user_is_denied."
            )
            continue
        minimum = entry.get("minimum_passed", len(tests))
        if type(minimum) is not int or minimum < len(tests):
            problems.append(f"Control registry entry {check_id} has a minimum_passed below its required tests.")
            continue
        if problem := pytest_command_problem(str(entry["command"])):
            problems.append(f"Control registry entry {check_id}: {problem}.")
            continue
        controls[check_id] = dict(entry, minimum_passed=minimum)
    return controls, problems


def pytest_command_problem(command: str) -> str:
    """Return why a registry command cannot produce a pytest report, or ''."""
    try:
        argv = shlex.split(command)
    except ValueError:
        return "the command cannot be parsed"
    if not argv:
        return "the command is empty"
    name = Path(argv[0]).name
    if name == "pytest":
        rest = argv[1:]
    elif name in {"python", "python3"} and argv[1:3] == ["-m", "pytest"]:
        rest = argv[3:]
    else:
        return "the command must start with pytest or python -m pytest"
    if information_only(argv):
        return "the command asks pytest for information instead of running tests"
    if any(arg.startswith("--junitxml") or arg.startswith("--junit-xml") for arg in rest):
        return "the command must not set --junitxml; the CI runner adds it"
    return ""


def registry_file_problems(root: Path, registry: Path, controls: dict[str, dict[str, Any]]) -> list[str]:
    """Check that the registry is owned in CODEOWNERS and that its test files exist."""
    problems = []
    try:
        relative = registry.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return [f"The control registry {registry} is outside the repository."]
    owners = [root / name for name in CODEOWNERS_PATHS if (root / name).is_file()]
    listed = False
    for path in owners:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.split("#", 1)[0].split()
            if len(parts) >= 2 and parts[0].lstrip("/") == relative:
                listed = True
    if not listed:
        problems.append(
            f"The control registry {relative} has no line of its own in CODEOWNERS, so a change to it may not "
            "need review. Add one, and require code-owner review."
        )
    for check_id, control in sorted(controls.items()):
        for test in control["required_tests"]:
            file = test.split("::", 1)[0]
            target = (root / file).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                problems.append(f"Control {check_id} requires {test}, but {file} is not in the repository.")
    return problems


def read_junit(report: Path, root: Path) -> dict[str, Any]:
    """Return each test's outcome from a pytest JUnit XML report."""
    try:
        tree = ElementTree.parse(report)
    except (OSError, ElementTree.ParseError) as exc:
        return {"problem": f"the test report cannot be read: {exc}"}
    outcomes: dict[str, str] = {}
    for case in tree.iter("testcase"):
        classname = case.get("classname") or ""
        name = case.get("name") or ""
        if case.find("failure") is not None or case.find("error") is not None:
            outcome = "failed"
        elif case.find("skipped") is not None:
            outcome = "skipped"
        else:
            outcome = "passed"
        outcomes[_test_id(classname, name, root)] = outcome
    counts = {key: sum(1 for value in outcomes.values() if value == key) for key in ("passed", "failed", "skipped")}
    return {"format": "junit", "tests": outcomes, "counts": counts}


def _test_id(classname: str, name: str, root: Path) -> str:
    """Find the module file for a JUnit classname, trying the longest prefix first."""
    parts = classname.split(".")
    for size in range(len(parts), 0, -1):
        candidate = "/".join(parts[:size]) + ".py"
        if (root / candidate).is_file():
            return "::".join([candidate, *parts[size:], name])
    return "::".join([classname, name])


def control_reasons(
    document: dict[str, Any],
    controls: dict[str, dict[str, Any]],
    critical_ids: set[str],
    evidence: dict[str, Any] | None,
) -> list[str]:
    """Compare passing checks with the registry and, in CI, with the test report."""
    reasons = []
    runs: dict[str, dict[str, Any]] = {}
    for run in (evidence or {}).get("runs") or []:
        if isinstance(run, dict):
            for item_id in run.get("ids") or []:
                runs[str(item_id)] = run
    for check in document.get("mandatory_checks") or []:
        check_id = str(check.get("id") or "")
        if check.get("status") != "PASS" or check.get("evidence_type") != "runtime":
            continue
        control = controls.get(check_id)
        if control is None:
            if check_id in critical_ids:
                reasons.append(
                    f"{check_id} is a critical check with no entry in the control registry, so no reviewed test "
                    "is bound to it."
                )
            continue
        if str(check.get("command") or "").strip() != control["command"].strip():
            reasons.append(f"{check_id} records a command that is not the one in the control registry.")
            continue
        if evidence is None:
            continue
        report = (runs.get(check_id) or {}).get("test_report")
        if not isinstance(report, dict):
            reasons.append(f"{check_id}: CI recorded no test report, so the required tests are not shown to have run.")
            continue
        if report.get("problem"):
            reasons.append(f"{check_id}: {report['problem']}.")
            continue
        outcomes = report.get("tests") or {}
        counts = report.get("counts") or {}
        if not outcomes:
            reasons.append(f"{check_id}: the test report shows that no tests ran.")
            continue
        missing = [test for test in control["required_tests"] if test not in outcomes]
        not_passed = [f"{test} {outcomes[test]}" for test in control["required_tests"] if outcomes.get(test) not in (None, "passed")]
        if missing:
            reasons.append(f"{check_id}: required tests did not run: {', '.join(missing)}.")
        if not_passed:
            reasons.append(f"{check_id}: required tests did not pass: {', '.join(not_passed)}.")
        if not missing and not not_passed and int(counts.get("passed") or 0) < control["minimum_passed"]:
            reasons.append(f"{check_id}: fewer than {control['minimum_passed']} tests passed.")
    return reasons

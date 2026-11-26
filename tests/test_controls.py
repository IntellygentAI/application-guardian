"""The release gate checks that the reviewed tests for each control ran and passed."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import guardian_controls  # noqa: E402
import guardianlib  # noqa: E402

INVENTORY = guardianlib.load_inventory()
CRITICAL = {item["id"] for item in INVENTORY if item["critical"]}
HAS_PYTEST = importlib.util.find_spec("pytest") is not None

COMMAND = "python -m pytest -q tests/security/test_invoices.py"
REQUIRED = [
    "tests/security/test_invoices.py::test_owner_can_read_invoice",
    "tests/security/test_invoices.py::test_other_user_is_denied",
    "tests/security/test_invoices.py::TestAnonymous::test_anonymous_is_denied",
]

INVOICE_TESTS = """from src.invoices import read


def test_owner_can_read_invoice():
    assert read("owner", "inv-1") == 200


def test_other_user_is_denied():
    assert read("other", "inv-1") == 404


class TestAnonymous:
    def test_anonymous_is_denied(self):
        assert read(None, "inv-1") == 404
"""

SKIPPED_TESTS = """import pytest

pytestmark = pytest.mark.skip(reason="not ready")


def test_owner_can_read_invoice():
    assert False


def test_other_user_is_denied():
    assert False


class TestAnonymous:
    def test_anonymous_is_denied(self):
        assert False
"""


def git(repo, *arguments):
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *arguments],
        check=True,
        capture_output=True,
    )


def registry(command=COMMAND, required=None, runner="pytest", only=None):
    controls = []
    for check_id in sorted(CRITICAL):
        if only is not None and check_id not in only:
            continue
        controls.append(
            {"check_id": check_id, "runner": runner, "command": command, "required_tests": list(required or REQUIRED)}
        )
    return {"schema_version": "1.0", "controls": controls}


def audit(commit, command=COMMAND):
    checks = []
    for item in INVENTORY:
        checks.append({
            "id": item["id"], "status": "PASS", "critical": item["critical"], "evidence_type": "runtime",
            "commit": commit, "command": command, "exit_code": 0, "observed": "3 passed",
            "executed_at": "2026-11-26T00:00:00Z",
        })
    return {
        "schema_version": "1.1", "commit": commit, "environment": "local", "executed_at": "2026-11-26T00:00:00Z",
        "findings": [], "mandatory_checks": checks, "accepted_risks": [],
    }


def evidence_for(outcomes, command=COMMAND, **report):
    """CI evidence with one passing run of COMMAND for every check."""
    test_report = {"format": "junit", "tests": outcomes,
                   "counts": {k: list(outcomes.values()).count(k) for k in ("passed", "failed", "skipped")}}
    test_report.update(report)
    run = {"ids": [item["id"] for item in INVENTORY], "command": command, "exit_code": 0, "test_report": test_report}
    return {"schema_version": "1.0", "commit": "abc123", "run_id": "1", "runs": [run]}


def reasons(document, controls, evidence=None):
    return " ".join(guardian_controls.control_reasons(document, controls, CRITICAL, evidence))


class ControlUnitTests(unittest.TestCase):
    """The rules, on recorded evidence."""

    def setUp(self):
        self.controls, problems = guardian_controls.load_registry_document(registry())
        self.assertEqual(problems, [])
        self.document = audit("abc123")
        self.passed = {test: "passed" for test in REQUIRED}

    def test_all_required_tests_passed_is_eligible_for_go(self):
        self.assertEqual(reasons(self.document, self.controls, evidence_for(self.passed)), "")

    def test_zero_tests_executed_is_no_go(self):
        self.assertIn("no tests ran", reasons(self.document, self.controls, evidence_for({})))

    def test_all_tests_skipped_is_no_go(self):
        skipped = {test: "skipped" for test in REQUIRED}
        self.assertIn("did not pass", reasons(self.document, self.controls, evidence_for(skipped)))

    def test_unrelated_tests_passed_is_no_go(self):
        unrelated = {"tests/test_health.py::test_health": "passed"}
        self.assertIn("required tests did not run", reasons(self.document, self.controls, evidence_for(unrelated)))

    def test_one_required_test_missing_is_no_go(self):
        partial = dict(self.passed)
        partial.pop(REQUIRED[2])
        self.assertIn("TestAnonymous::test_anonymous_is_denied", reasons(self.document, self.controls, evidence_for(partial)))

    def test_required_test_failed_is_no_go(self):
        failed = dict(self.passed, **{REQUIRED[1]: "failed"})
        self.assertIn("test_other_user_is_denied failed", reasons(self.document, self.controls, evidence_for(failed)))

    def test_missing_or_broken_report_is_no_go(self):
        evidence = evidence_for(self.passed)
        del evidence["runs"][0]["test_report"]
        self.assertIn("no test report", reasons(self.document, self.controls, evidence))
        broken = evidence_for(self.passed, problem="pytest wrote no test report")
        self.assertIn("pytest wrote no test report", reasons(self.document, self.controls, broken))

    def test_audit_command_must_match_the_registry(self):
        other = audit("abc123", command="python -m pytest -q tests/test_health.py")
        self.assertIn("not the one in the control registry", reasons(other, self.controls))

    def test_critical_check_without_a_control_is_no_go(self):
        controls, _ = guardian_controls.load_registry_document(registry(only={"ownership"}))
        self.assertIn("secrets is a critical check with no entry", reasons(self.document, controls))

    def test_registry_rejects_bad_entries(self):
        cases = {
            "uses runner 'jest'": registry(runner="jest"),
            "asks pytest for information": registry(command="python -m pytest --version"),
            "must not set --junitxml": registry(command="pytest --junitxml=x.xml tests"),
            "must start with pytest": registry(command="npm test"),
            "pytest test IDs": registry(required=["test_owner_can_read_invoice"]),
        }
        for expected, document in cases.items():
            _, problems = guardian_controls.load_registry_document(document)
            self.assertIn(expected, " ".join(problems), expected)

    def test_version_and_help_commands_cannot_prove_a_check(self):
        for command in ("pytest --version", "npm --version", "go version", "node --version", "python -m this",
                        "pytest --help", "pytest --collect-only", "python", "jest --listTests"):
            problem = guardianlib.test_command_problem(command, guardianlib.TEST_RUNNERS | {"jest"})
            self.assertTrue(problem, command)
        for command in ("pytest tests/test_a.py", "python -m pytest -q", "python -m unittest -q tests", "python run_tests.py"):
            self.assertEqual(guardianlib.test_command_problem(command, guardianlib.TEST_RUNNERS), "", command)

    def test_template_registry_is_valid(self):
        _, problems = guardian_controls.load_registry(ROOT / "templates" / "ci" / "guardian-checks.json")
        self.assertEqual(problems, [])

    def test_junit_report_ids_match_pytest_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests" / "security").mkdir(parents=True)
            (root / "tests" / "security" / "test_invoices.py").write_text("", encoding="utf-8")
            report = root / "report.xml"
            report.write_text(
                '<testsuites><testsuite tests="4">'
                '<testcase classname="tests.security.test_invoices" name="test_owner_can_read_invoice"/>'
                '<testcase classname="tests.security.test_invoices" name="test_other_user_is_denied"><failure/></testcase>'
                '<testcase classname="tests.security.test_invoices.TestAnonymous" name="test_anonymous_is_denied">'
                '<skipped/></testcase>'
                '<testcase classname="tests.security.test_invoices" name="test_case[a-1]"><error/></testcase>'
                "</testsuite></testsuites>",
                encoding="utf-8",
            )
            result = guardian_controls.read_junit(report, root)
        self.assertEqual(result["tests"], {
            REQUIRED[0]: "passed", REQUIRED[1]: "failed", REQUIRED[2]: "skipped",
            "tests/security/test_invoices.py::test_case[a-1]": "failed",
        })


@unittest.skipUnless(HAS_PYTEST, "needs pytest to produce real reports")
class ControlEndToEndTests(unittest.TestCase):
    """ci_evidence.py runs pytest with a report; the gate reads what it recorded."""

    def build(self, tmp, tests=INVOICE_TESTS, owners=True, controls=None, command=COMMAND):
        repo = Path(tmp) / "repo"
        (repo / "src").mkdir(parents=True)
        (repo / "tests" / "security").mkdir(parents=True)
        (repo / "docs" / "audits").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (repo / ".gitignore").write_text("__pycache__/\n.pytest_cache/\n", encoding="utf-8")
        (repo / "src" / "__init__.py").write_text("", encoding="utf-8")
        (repo / "src" / "invoices.py").write_text(
            "def read(user, invoice):\n    return 200 if user == 'owner' else 404\n", encoding="utf-8"
        )
        (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
        (repo / "tests" / "security" / "__init__.py").write_text("", encoding="utf-8")
        (repo / "tests" / "security" / "test_invoices.py").write_text(tests, encoding="utf-8")
        (repo / "tests" / "test_health.py").write_text("def test_health():\n    assert True\n", encoding="utf-8")
        if owners:
            (repo / ".github").mkdir()
            (repo / ".github" / "CODEOWNERS").write_text("/guardian-checks.json @org/release\n", encoding="utf-8")
        (repo / "guardian-checks.json").write_text(json.dumps(controls or registry()), encoding="utf-8")
        path = repo / "docs" / "audits" / "audit-result.json"
        path.write_text("{}", encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "app")
        head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        path.write_text(json.dumps(audit(head, command)), encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "audit")
        return repo, path, Path(tmp) / "evidence"

    def env(self):
        environment = {key: value for key, value in os.environ.items() if not key.startswith("GITHUB_")}
        environment["GITHUB_RUN_ID"] = "1"
        return environment

    def run_both(self, repo, path, out, before=None):
        registry_path = repo / "guardian-checks.json"
        if before:
            before(out)
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "ci_evidence.py"), str(path), "--out", str(out),
             "--controls", str(registry_path)],
            env=self.env(), capture_output=True, text=True, check=False, cwd=repo,
        )
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "release_gate.py"), str(path),
             "--ci-evidence", str(out / "ci-evidence.json"), "--controls", str(registry_path)],
            env=self.env(), capture_output=True, text=True, check=False, cwd=repo,
        )

    def test_required_tests_pass_gives_go(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, path, out = self.build(tmp)
            completed = self.run_both(repo, path, out)
            evidence = json.loads((out / "ci-evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(completed.stdout.splitlines()[0], "GO", completed.stdout + completed.stderr)
        self.assertEqual(evidence["runs"][0]["test_report"]["counts"]["passed"], 3)

    def test_all_skipped_tests_exit_zero_but_are_no_go(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, path, out = self.build(tmp, tests=SKIPPED_TESTS)
            completed = self.run_both(repo, path, out)
        self.assertEqual(completed.returncode, 1, completed.stdout)
        self.assertIn("did not pass", completed.stdout)
        self.assertNotIn("exited", completed.stdout)

    def test_unrelated_passing_tests_are_no_go(self):
        unrelated = "python -m pytest -q tests/test_health.py"
        with tempfile.TemporaryDirectory() as tmp:
            repo, path, out = self.build(tmp, controls=registry(command=unrelated), command=unrelated)
            completed = self.run_both(repo, path, out)
        self.assertEqual(completed.returncode, 1, completed.stdout)
        self.assertIn("required tests did not run", completed.stdout)

    def test_report_left_from_an_earlier_run_does_not_count(self):
        stale = (
            '<testsuites><testsuite>'
            + "".join(f'<testcase classname="tests.security.test_invoices" name="{t.split("::")[-1]}"/>' for t in REQUIRED)
            + "</testsuite></testsuites>"
        )

        def plant(out):
            (out / "reports").mkdir(parents=True)
            (out / "reports" / "run-001.xml").write_text(stale, encoding="utf-8")

        broken = "python -m pytest -q -p no:junitxml tests/security/test_invoices.py"
        with tempfile.TemporaryDirectory() as tmp:
            repo, path, out = self.build(tmp, controls=registry(command=broken), command=broken)
            completed = self.run_both(repo, path, out, before=plant)
        self.assertEqual(completed.returncode, 1, completed.stdout)
        self.assertIn("pytest wrote no test report", completed.stdout)

    def test_registry_not_in_codeowners_is_no_go(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, path, out = self.build(tmp, owners=False)
            completed = self.run_both(repo, path, out)
        self.assertEqual(completed.returncode, 1, completed.stdout)
        self.assertIn("no line of its own in CODEOWNERS", completed.stdout)

    def test_uncommitted_registry_change_is_no_go(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, path, out = self.build(tmp)
            (repo / "guardian-checks.json").write_text(json.dumps(registry(required=REQUIRED[:1])), encoding="utf-8")
            completed = self.run_both(repo, path, out)
        self.assertEqual(completed.returncode, 1, completed.stdout)
        self.assertIn("guardian-checks.json", completed.stdout)


if __name__ == "__main__":
    unittest.main()

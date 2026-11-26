import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import detect_stack  # noqa: E402
import guardianlib  # noqa: E402
import release_gate  # noqa: E402
import scaffold_audit  # noqa: E402
import validate_report  # noqa: E402
import validate_skill  # noqa: E402


def document(**overrides):
    base = {
        "schema_version": "1.0",
        "commit": "abc123",
        "environment": "local",
        "executed_at": "2026-11-26T00:00:00Z",
        "findings": [],
        "mandatory_checks": [
            {
                "id": "auth",
                "status": "PASS",
                "critical": True,
                "evidence_type": "runtime",
            }
        ],
        "accepted_risks": [],
    }
    base.update(overrides)
    return base


class ReleaseGateTests(unittest.TestCase):
    def test_go_when_runtime_checks_pass(self):
        result = guardianlib.decide(document())
        self.assertEqual(result["release_decision"], "GO")
        self.assertEqual(release_gate.evaluate(document(), strict=False), 0)

    def test_no_go_for_open_high_finding(self):
        report = document(
            findings=[
                {
                    "id": "AG-001",
                    "title": "Cross-user invoice read",
                    "severity": "high",
                    "status": "open",
                    "evidence_type": "runtime",
                }
            ]
        )
        self.assertEqual(guardianlib.decide(report)["release_decision"], "NO-GO")
        self.assertEqual(release_gate.evaluate(report, strict=False), 1)

    def test_critical_cannot_be_accepted(self):
        report = document(
            findings=[
                {
                    "id": "AG-002",
                    "title": "Exposed service credential",
                    "severity": "critical",
                    "status": "accepted",
                    "evidence_type": "static",
                }
            ],
            accepted_risks=["AG-002"],
        )
        self.assertEqual(guardianlib.decide(report)["release_decision"], "NO-GO")

    def test_static_evidence_does_not_pass_a_critical_control(self):
        report = document(
            mandatory_checks=[
                {
                    "id": "rls",
                    "status": "PASS",
                    "critical": True,
                    "evidence_type": "static",
                }
            ]
        )
        self.assertEqual(guardianlib.decide(report)["release_decision"], "NO-GO")

    def test_stale_commit_is_no_go(self):
        report = document(head_commit="def456")
        self.assertEqual(guardianlib.decide(report)["release_decision"], "NO-GO")

    def test_unaccepted_medium_is_no_go(self):
        report = document(
            findings=[
                {
                    "id": "AG-003",
                    "title": "Missing rate limit",
                    "severity": "medium",
                    "status": "open",
                    "evidence_type": "static",
                }
            ]
        )
        self.assertEqual(guardianlib.decide(report)["release_decision"], "NO-GO")

    def test_accepted_medium_is_conditional(self):
        report = document(
            findings=[
                {
                    "id": "AG-003",
                    "title": "Missing rate limit",
                    "severity": "medium",
                    "status": "accepted",
                    "evidence_type": "static",
                }
            ],
            accepted_risks=["AG-003"],
        )
        result = guardianlib.decide(report)
        self.assertEqual(result["release_decision"], "CONDITIONAL GO")
        self.assertEqual(release_gate.evaluate(report, strict=False), 0)
        self.assertEqual(release_gate.evaluate(report, strict=True), 1)

    def test_empty_checklist_is_no_go(self):
        self.assertEqual(guardianlib.decide(document(mandatory_checks=[]))["release_decision"], "NO-GO")

    def test_failed_mandatory_check_is_no_go(self):
        report = document(
            mandatory_checks=[
                {
                    "id": "payment",
                    "status": "FAIL",
                    "critical": True,
                    "evidence_type": "runtime",
                }
            ]
        )
        self.assertEqual(guardianlib.decide(report)["release_decision"], "NO-GO")

    def test_invalid_document_exits_2(self):
        self.assertEqual(release_gate.evaluate({"schema_version": "1.0"}, strict=False), 2)

    def test_fixed_critical_needs_runtime_evidence(self):
        finding = {
            "id": "AG-1",
            "title": "Cross-user invoice read",
            "severity": "critical",
            "status": "fixed",
            "evidence_type": "static",
        }
        result = guardianlib.decide(document(findings=[finding]))
        self.assertEqual(result["release_decision"], "NO-GO")
        finding["evidence_type"] = "runtime"
        self.assertEqual(guardianlib.decide(document(findings=[finding]))["release_decision"], "GO")

    def test_check_from_older_commit_is_stale(self):
        check = {"id": "auth", "status": "PASS", "critical": True, "evidence_type": "runtime", "commit": "old000"}
        result = guardianlib.decide(document(mandatory_checks=[check], head_commit="abc123"))
        self.assertEqual(result["release_decision"], "NO-GO")

    def test_cli_head_overrides_head_written_in_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "audit-result.json"
            path.write_text(json.dumps(document(head_commit="abc123")), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "release_gate.py"), str(path), "--head", "def456"],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("stale", completed.stdout)

    def test_sample_audit_is_no_go(self):
        sample = json.loads((ROOT / "examples" / "sample-audit-result.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_report.validate_audit(sample), [])
        self.assertEqual(release_gate.evaluate(sample, strict=False), 1)

    def test_false_go_fixture_is_no_go(self):
        sample = json.loads(
            (ROOT / "evals" / "fixtures" / "false-go" / "audit-result.json").read_text(encoding="utf-8")
        )
        self.assertEqual(guardianlib.decide(sample)["release_decision"], "NO-GO")


class ScaffoldTests(unittest.TestCase):
    def test_scaffold_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp)
            self.assertEqual(scaffold_audit.scaffold(destination), 0)
            target = destination / "application-audit.md"
            target.write_text("keep me", encoding="utf-8")
            self.assertEqual(scaffold_audit.scaffold(destination), 0)
            self.assertEqual(target.read_text(encoding="utf-8"), "keep me")
            self.assertTrue((destination / "audit-result.json").is_file())


class StackTests(unittest.TestCase):
    def test_detects_next_and_supabase(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(
                json.dumps({"dependencies": {"next": "14.0.0", "@supabase/supabase-js": "2.0.0"}}),
                encoding="utf-8",
            )
            found = detect_stack.detect(root)
            self.assertIn("nextjs", found)
            self.assertIn("react", found)
            self.assertIn("supabase", found)


class SkillValidationTests(unittest.TestCase):
    def test_repository_skill_is_valid(self):
        self.assertEqual(validate_skill.validate(), [])

    def test_evals_are_unmeasured_and_complete(self):
        catalog = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["measurement_status"], "not_measured")
        self.assertGreaterEqual(len(catalog["cases"]), 12)
        for case in catalog["cases"]:
            self.assertIsNone(case["agent_result"])
            expected = ROOT / case["expected"]
            self.assertTrue(expected.is_file(), case["id"])
            if case["fixture"] is not None:
                self.assertTrue((ROOT / case["fixture"]).is_file(), case["id"])


class CliTests(unittest.TestCase):
    def test_release_gate_cli_on_sample(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "release_gate.py"), str(ROOT / "examples" / "sample-audit-result.json")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("NO-GO", completed.stdout)


if __name__ == "__main__":
    unittest.main()

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

COMMIT = "abc123"
INVENTORY = guardianlib.load_inventory()


def passing_check(check_id, critical, commit=COMMIT):
    return {
        "id": check_id,
        "status": "PASS",
        "critical": critical,
        "evidence_type": "runtime",
        "commit": commit,
        "command": f"pytest tests/release/test_{check_id.replace('-', '_')}.py",
        "exit_code": 0,
        "expected": "allowed and denied cases behave as specified",
        "observed": "all tests passed",
        "executed_at": "2026-11-26T00:00:00Z",
    }


def all_checks(commit=COMMIT):
    return [passing_check(item["id"], item["critical"], commit) for item in INVENTORY]


def with_check(**fields):
    """Every mandatory check passes, except the one replaced by fields."""
    checks = all_checks()
    for index, check in enumerate(checks):
        if check["id"] == fields["id"]:
            checks[index] = {key: value for key, value in fields.items() if value is not None}
    return checks


def document(**overrides):
    base = {
        "schema_version": "1.1",
        "commit": COMMIT,
        "environment": "local",
        "executed_at": "2026-11-26T00:00:00Z",
        "findings": [],
        "mandatory_checks": all_checks(),
        "accepted_risks": [],
    }
    base.update(overrides)
    return base


def fixed_finding(**overrides):
    finding = {
        "id": "AG-1",
        "title": "Cross-user invoice read",
        "severity": "critical",
        "status": "fixed",
        "evidence_type": "runtime",
        "commit": COMMIT,
        "command": "pytest tests/test_invoices.py::test_other_user_cannot_read",
        "exit_code": 0,
        "observed": "HTTP 404 for the other synthetic user",
        "executed_at": "2026-11-26T00:00:00Z",
    }
    finding.update(overrides)
    return finding


def risk(risk_id="AG-3", **overrides):
    record = {
        "id": risk_id,
        "owner": "payments team",
        "approved_by": "A. Maintainer",
        "approved_at": "2026-11-26",
        "reason": "Rate limit lands in the next sprint; abuse is monitored.",
    }
    record.update(overrides)
    return record


def medium_finding(status="accepted"):
    return {
        "id": "AG-3",
        "title": "Missing rate limit",
        "severity": "medium",
        "status": status,
        "evidence_type": "static",
    }


def decision(report, **kwargs):
    return guardianlib.decide(report, **kwargs)["release_decision"]


def reasons(report, **kwargs):
    return " ".join(guardianlib.decide(report, **kwargs)["reasons"])


def run_gate(path, *extra, cwd=None):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "release_gate.py"), str(path), *extra],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def git(repo, *arguments):
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *arguments],
        check=True,
        capture_output=True,
    )


def head_of(repo):
    return subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()


class ReleaseGateTests(unittest.TestCase):
    def test_go_when_every_mandatory_check_passes(self):
        self.assertEqual(decision(document()), "GO")
        self.assertEqual(release_gate.evaluate(document(), strict=False), 0)

    def test_no_go_for_open_high_finding(self):
        report = document(findings=[fixed_finding(id="AG-001", severity="high", status="open")])
        self.assertEqual(decision(report), "NO-GO")
        self.assertEqual(release_gate.evaluate(report, strict=False), 1)

    def test_critical_cannot_be_accepted(self):
        finding = fixed_finding(id="AG-3", status="accepted")
        self.assertEqual(decision(document(findings=[finding], accepted_risks=[risk()])), "NO-GO")

    def test_static_evidence_does_not_pass_a_critical_control(self):
        report = document(mandatory_checks=with_check(id="database-policies", status="PASS", critical=True,
                                                      evidence_type="static", commit=COMMIT, observed="policy read"))
        self.assertEqual(decision(report), "NO-GO")

    def test_stale_commit_is_no_go(self):
        self.assertEqual(decision(document(head_commit="def456")), "NO-GO")

    def test_unaccepted_medium_is_no_go(self):
        self.assertEqual(decision(document(findings=[medium_finding("open")])), "NO-GO")

    def test_accepted_medium_with_approval_is_conditional(self):
        report = document(findings=[medium_finding()], accepted_risks=[risk()])
        self.assertEqual(decision(report), "CONDITIONAL GO")
        self.assertEqual(release_gate.evaluate(report, strict=False), 0)
        self.assertEqual(release_gate.evaluate(report, strict=True), 1)

    def test_empty_checklist_is_no_go(self):
        self.assertEqual(decision(document(mandatory_checks=[])), "NO-GO")

    def test_failed_mandatory_check_is_no_go(self):
        report = document(mandatory_checks=with_check(**dict(passing_check("payment-verification", True),
                                                             status="FAIL", exit_code=1)))
        self.assertEqual(decision(report), "NO-GO")

    def test_invalid_document_exits_2(self):
        self.assertEqual(release_gate.evaluate({"schema_version": "1.1"}, strict=False), 2)

    def test_old_schema_version_is_rejected(self):
        self.assertEqual(release_gate.evaluate(document(schema_version="1.0"), strict=False), 2)

    def test_fixed_critical_needs_runtime_evidence(self):
        self.assertEqual(decision(document(findings=[fixed_finding(evidence_type="static")])), "NO-GO")
        self.assertEqual(decision(document(findings=[fixed_finding()])), "GO")

    def test_pass_without_commit_is_not_fresh(self):
        report = document(mandatory_checks=with_check(**dict(passing_check("authentication", True), commit=None)))
        self.assertIn("no recorded commit", reasons(report))
        self.assertEqual(decision(report), "NO-GO")

    def test_check_from_older_commit_is_stale(self):
        report = document(mandatory_checks=with_check(**passing_check("authentication", True, commit="old000")))
        self.assertEqual(decision(report), "NO-GO")

    # Mandatory-check inventory

    def test_missing_mandatory_check_is_no_go(self):
        checks = [check for check in all_checks() if check["id"] != "tenant-isolation"]
        report = document(mandatory_checks=checks)
        self.assertEqual(decision(report), "NO-GO")
        self.assertIn("tenant-isolation", reasons(report))

    def test_one_passing_check_cannot_stand_for_the_release(self):
        report = document(mandatory_checks=[passing_check("authentication", True)])
        self.assertIn("24 mandatory check(s) are missing", reasons(report))

    def test_duplicate_check_id_is_no_go(self):
        report = document(mandatory_checks=all_checks() + [passing_check("secrets", True)])
        self.assertIn("appears 2 times", reasons(report))

    def test_critical_check_cannot_be_downgraded(self):
        report = document(mandatory_checks=with_check(**passing_check("ownership", False)))
        self.assertIn("cannot be recorded as non-critical", reasons(report))

    def test_not_applicable_needs_justification(self):
        bare = {"id": "payment-verification", "status": "NOT APPLICABLE", "critical": True, "evidence_type": "none"}
        self.assertEqual(decision(document(mandatory_checks=with_check(**bare))), "NO-GO")
        justified = dict(bare, justification="The application takes no payments.")
        self.assertEqual(decision(document(mandatory_checks=with_check(**justified))), "GO")

    # Runtime evidence fields

    def test_runtime_pass_needs_command_exit_code_and_observation(self):
        for field, value in (("command", None), ("exit_code", 1), ("exit_code", None), ("observed", None),
                             ("executed_at", None)):
            check = dict(passing_check("authentication", True), **{field: value})
            report = document(mandatory_checks=with_check(**check))
            self.assertEqual(decision(report), "NO-GO", field)

    def test_static_pass_needs_observation(self):
        check = {"id": "layouts", "status": "PASS", "critical": False, "evidence_type": "static", "commit": COMMIT}
        self.assertEqual(decision(document(mandatory_checks=with_check(**check))), "NO-GO")
        check["observed"] = "Reviewed at 320 px and 1440 px; no clipped controls"
        self.assertEqual(decision(document(mandatory_checks=with_check(**check))), "GO")

    # Fixed findings are verified on the current commit

    def test_fixed_critical_from_older_commit_is_no_go(self):
        report = document(findings=[fixed_finding(commit="old000")])
        self.assertIn("commit abc123", reasons(report))
        self.assertEqual(decision(report), "NO-GO")

    def test_fixed_critical_needs_a_passing_run(self):
        for field, value in (("command", None), ("exit_code", 1), ("observed", None)):
            report = document(findings=[fixed_finding(**{field: value})])
            self.assertEqual(decision(report), "NO-GO", field)

    # Accepted risks need an owner and an approval record

    def test_accepted_risk_without_approval_is_invalid(self):
        report = document(findings=[medium_finding()], accepted_risks=["AG-3"])
        self.assertEqual(release_gate.evaluate(report, strict=False), 2)
        self.assertEqual(decision(report), "NO-GO")
        report = document(findings=[medium_finding()], accepted_risks=[risk(approved_by="")])
        self.assertEqual(release_gate.evaluate(report, strict=False), 2)
        self.assertEqual(decision(report), "NO-GO")

    def test_risk_record_must_match_an_accepted_finding(self):
        report = document(accepted_risks=[risk("AG-99")])
        self.assertIn("does not match an accepted finding", reasons(report))

    # Working tree

    def test_worktree_changes_block_release(self):
        report = document()
        self.assertEqual(decision(report, worktree_changes=["app/api/invoices.ts"]), "NO-GO")
        self.assertIn("app/api/invoices.ts", reasons(report, worktree_changes=["app/api/invoices.ts"]))

    def test_cli_detects_uncommitted_code_but_ignores_the_audit_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", tmp], check=True)
            (repo / "app.py").write_text("print('v1')\n", encoding="utf-8")
            audits = repo / "docs" / "audits"
            audits.mkdir(parents=True)
            path = audits / "audit-result.json"
            path.write_text("{}", encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "app")
            head = head_of(repo)
            path.write_text(json.dumps(document(commit=head, mandatory_checks=all_checks(head))), encoding="utf-8")
            (audits / "application-audit.md").write_text("report", encoding="utf-8")
            clean = run_gate(path)
            (repo / "app.py").write_text("print('v2')\n", encoding="utf-8")
            dirty = run_gate(path)
            (repo / "app.py").write_text("print('v1')\n", encoding="utf-8")
            (repo / "new_route.py").write_text("route\n", encoding="utf-8")
            untracked = run_gate(path)
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
        self.assertEqual(dirty.returncode, 1)
        self.assertIn("app.py", dirty.stdout)
        self.assertEqual(untracked.returncode, 1)
        self.assertIn("new_route.py", untracked.stdout)

    # Command line and HEAD

    def test_cli_without_head_outside_git_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "audit-result.json"
            path.write_text(json.dumps(document()), encoding="utf-8")
            completed = run_gate(path, cwd=tmp)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("--head", completed.stderr)

    def test_cli_without_head_reads_git_head(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", tmp], check=True)
            path = repo / "audit-result.json"
            path.write_text(json.dumps(document(head_commit=COMMIT)), encoding="utf-8")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "audit")
            head = head_of(repo)
            stale = run_gate(path)
            path.write_text(json.dumps(document(commit=head, mandatory_checks=all_checks(head))), encoding="utf-8")
            fresh = run_gate(path)
        self.assertEqual(stale.returncode, 1)
        self.assertIn("stale", stale.stdout)
        self.assertEqual(fresh.returncode, 0, fresh.stdout + fresh.stderr)

    def test_cli_head_overrides_head_written_in_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "audit-result.json"
            path.write_text(json.dumps(document(head_commit=COMMIT)), encoding="utf-8")
            completed = run_gate(path, "--head", "def456")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("stale", completed.stdout)

    def test_sample_audit_is_no_go_for_its_own_findings(self):
        sample = json.loads((ROOT / "examples" / "sample-audit-result.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_report.validate_audit(sample), [])
        result = guardianlib.decide(sample)
        self.assertEqual(result["release_decision"], "NO-GO")
        self.assertEqual(result["reasons"], ["AG-001 is an unresolved high finding.", "ownership failed."])

    def test_false_go_fixture_is_no_go(self):
        sample = json.loads(
            (ROOT / "evals" / "fixtures" / "false-go" / "audit-result.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_report.validate_audit(sample), [])
        self.assertEqual(decision(sample), "NO-GO")


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

    def test_scaffold_lists_every_mandatory_check_as_not_tested(self):
        with tempfile.TemporaryDirectory() as tmp:
            scaffold_audit.scaffold(Path(tmp))
            started = json.loads((Path(tmp) / "audit-result.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_report.validate_audit(dict(started, commit=COMMIT)), [])
        self.assertEqual([check["id"] for check in started["mandatory_checks"]], [item["id"] for item in INVENTORY])
        self.assertTrue(all(check["status"] == "NOT TESTED" for check in started["mandatory_checks"]))
        self.assertEqual(decision(started), "NO-GO")

    def test_checklist_template_lists_every_mandatory_check(self):
        checklist = (ROOT / "templates" / "release-checklist.md").read_text(encoding="utf-8")
        for item in INVENTORY:
            self.assertIn(f"`{item['id']}`", checklist, item["id"])


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

    def test_pyproject_reads_dependencies_not_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                "# Migrated away from Django and Stripe.\n"
                "[project]\n"
                'name = "svc"\n'
                'description = "Replaces the old Django admin"\n'
                'dependencies = ["fastapi>=0.110", "sqlalchemy[asyncio]~=2.0"]\n'
                "[tool.poetry.group.billing.dependencies]\n"
                'stripe = "^9"\n',
                encoding="utf-8",
            )
            found = detect_stack.detect(root)
            self.assertIn("fastapi", found)
            self.assertIn("stripe", found)
            self.assertNotIn("django", found)


class SkillValidationTests(unittest.TestCase):
    def test_repository_skill_is_valid(self):
        self.assertEqual(validate_skill.validate(), [])

    def test_eval_catalogue_is_complete(self):
        catalog = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(catalog["cases"]), 12)
        for case in catalog["cases"]:
            self.assertIsNone(case["agent_result"])
            expected = ROOT / case["expected"]
            self.assertTrue(expected.is_file(), case["id"])
            if case["fixture"] is not None:
                self.assertTrue((ROOT / case["fixture"]).is_file(), case["id"])


class CliTests(unittest.TestCase):
    def test_release_gate_cli_on_sample(self):
        completed = run_gate(ROOT / "examples" / "sample-audit-result.json", "--head", "example0001", cwd=ROOT)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("NO-GO", completed.stdout)
        self.assertIn("ownership failed.", completed.stdout)


if __name__ == "__main__":
    unittest.main()

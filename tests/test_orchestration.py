import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OrchestrationTests(unittest.TestCase):
    def test_every_task_starts_with_orchestration(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("- [ ] Pin down the task and collect context", skill)
        self.assertIn("(references/orchestration.md)", skill)
        guide = (ROOT / "references" / "orchestration.md").read_text(encoding="utf-8")
        for heading in (
            "## 1. Pin down the task",
            "## 2. Collect context before reasoning",
            "## 5. Keep a coverage list",
            "## 8. Stop and ask",
        ):
            self.assertIn(heading, guide)
        report = (ROOT / "templates" / "audit-report.md").read_text(encoding="utf-8")
        self.assertIn("Coverage:", report)


if __name__ == "__main__":
    unittest.main()

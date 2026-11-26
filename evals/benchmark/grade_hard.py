#!/usr/bin/env python3
"""Grade hard-benchmark outputs mechanically against the key from hard_pack.py.

Every check is a fixed rule. No model or person scores the answers.

- A vulnerable case passes "detected" when the answer reports a finding, and
  "severity_within_one" when its severity is within one level of the key.
- A secure decoy passes "no_false_positive" when the answer reports no finding.
- An audit case passes "decision" when the release decision matches the key.

Usage:
    python evals/benchmark/grade_hard.py --key KEY.json --outputs DIR [--detail]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RANK = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def grade_case(expected: dict, answer: dict) -> dict[str, bool]:
    finding = answer.get("finding") is True
    if expected["kind"] == "gate":
        return {"decision": answer.get("decision") == expected["decision"]}
    if expected["finding"]:
        got = RANK.get(str(answer.get("severity", "none")).lower(), 0)
        return {"detected": finding, "severity_within_one": finding and abs(got - RANK[expected["severity"]]) <= 1}
    return {"no_false_positive": not finding}


def grade(key: dict, outputs: Path) -> dict:
    runs = {}
    for path in sorted(outputs.glob("*-[0-9].json")):
        answers = {a.get("case"): a for a in json.loads(path.read_text(encoding="utf-8"))}
        runs[path.stem] = {name: grade_case(key[name], answers.get(name, {})) for name in sorted(key)}
    summary: dict[str, dict] = {}
    for run, cases in runs.items():
        totals = summary.setdefault(run.rsplit("-", 1)[0], {"runs": 0, "checks": {}, "by_case": {}})
        totals["runs"] += 1
        for name, checks in cases.items():
            case_id = key[name]["id"]
            for check, ok in checks.items():
                passed, count = totals["checks"].get(check, [0, 0])
                totals["checks"][check] = [passed + int(ok), count + 1]
                passed, count = totals["by_case"].get(case_id, [0, 0])
                totals["by_case"][case_id] = [passed + int(ok), count + 1]
    for totals in summary.values():
        totals["total"] = [sum(v[0] for v in totals["checks"].values()), sum(v[1] for v in totals["checks"].values())]
    misses = {
        run: [[key[name]["id"], check] for name, checks in cases.items() for check, ok in checks.items() if not ok]
        for run, cases in runs.items()
    }
    return {"summary": summary, "misses": misses, "runs": runs}


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade hard-benchmark outputs.")
    parser.add_argument("--key", type=Path, required=True, help="Answer key written by hard_pack.py")
    parser.add_argument("--outputs", type=Path, required=True, help="Directory of <arm>-<run>.json files")
    parser.add_argument("--detail", action="store_true", help="Include every graded check per case")
    args = parser.parse_args()
    result = grade(json.loads(args.key.read_text(encoding="utf-8")), args.outputs)
    if not args.detail:
        result.pop("runs")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

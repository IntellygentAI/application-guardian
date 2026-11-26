# Benchmarks

## 2026-11-26: with and without the skill

**Result: on the 18 current eval cases, the skill made no measurable difference to correctness. Both arms passed all 96 graded checks.** The cases are too easy for the model tested. They show the skill does no harm on these cases, and that it adds cost. They cannot show that it improves detection.

| | Without the skill | With the skill |
| --- | --- | --- |
| Runs | 3 | 3 |
| Graded checks passed | 96 / 96 | 96 / 96 |
| Defects detected | 30 / 30 | 30 / 30 |
| Severity within one level | 30 / 30 | 30 / 30 |
| False positives on secure code | 0 / 12 | 0 / 12 |
| Correct NO-GO on a false or premature GO | 6 / 6 | 6 / 6 |
| Missing environment recorded as NOT TESTED or BLOCKED, not PASS | 3 / 3 | 3 / 3 |
| Documentation-only change: no finding, no full audit | 3 / 3 | 3 / 3 |
| Secret value repeated in the report | 0 / 3 | 0 / 3 |
| Exploit payload in an SQL report | 0 / 6 | 0 / 6 |
| Mean tokens per run | 48,432 | 60,349 (+25%) |
| Mean tool calls per run | 3.0 | 6.7 |
| Mean time per run | 35.6 s | 58.5 s (+64%) |

### Observations outside the score

These differences were noticed after reading the answers, so they were not part of the grading rules. Each was then counted by a text match over the summaries. They are reported, not scored.

| Behaviour | Without the skill | With the skill |
| --- | --- | --- |
| On the two secure-code cases, says a runtime test is still needed before the check can PASS | 0 / 6 | 6 / 6 |
| On the two audit-file cases, runs `release_gate.py` | 0 / 6 | 6 / 6 |
| On the two audit-file cases, reports the missing mandatory checks | 0 / 6 | 6 / 6 |
| Rates an unauthenticated IDOR on invoices as critical rather than high | 0 / 3 | 3 / 3 |
| Summaries that cite a CWE or WCAG reference (out of 54 per arm) | 1 | 10 |

Both arms named the missing idempotency key in the retry case (3 / 3 each), so that case did not separate them. The skill's effect on these cases is on evidence discipline, not on finding the defect: it stops a clean static review from being treated as a PASS, and it makes the agent compute the release decision rather than reason about it.

### Method

- **Model:** Claude Opus 5.5 for every run. One fresh agent per run, with file and shell tools, all 18 cases in one session.
- **Cases:** built by [`evals/benchmark/build_pack.py`](../evals/benchmark/build_pack.py) from [`evals/evals.json`](../evals/evals.json). Case folders have neutral names in a fixed shuffled order. The "Synthetic fixture" comments that describe each defect were removed. The secret case uses a fake service-role JWT built at run time.
- **Prompts:** identical except one paragraph that points the skill arm at `SKILL.md`. See [`evals/benchmark/prompts.md`](../evals/benchmark/prompts.md).
- **Isolation:** the answer key and every copy of this repository were moved out of the agents' reach during the runs. The skill arm received only `SKILL.md`, `references/`, `scripts/`, `schemas/`, and `templates/`.
- **Skill under test:** the skill files in the change that added this page, byte for byte.
- **Grading:** fixed rules in [`evals/benchmark/grade.py`](../evals/benchmark/grade.py) against the files in `evals/expected-results/`. No person or model scored the answers.
- **Raw data:** every answer, the key, per-run cost, and the grading output are in `evals/benchmark/results/2026-11-26/`, with the scores in [`grade.json`](../evals/benchmark/results/2026-11-26/grade.json).

### Limits

- Three runs per arm, one model, one harness. Small differences would not show.
- The cases are single files of a few lines with one clear defect each. Real audits are larger, have several defects, and include code that looks wrong but is fine.
- The skill arm was told to use the skill. Activation, whether an agent chooses the skill on its own, was not measured.
- The grading checks the structured answer. It does not judge the quality of the remediation advice.

### What would make the next run informative

- Cases where the defect is not visible in the file under review: authorisation in middleware that a route bypasses, a policy in a migration, a price looked up in one function and overwritten in another.
- Multi-file cases with more than one defect and with decoys that are secure.
- Audit files where the gate must catch subtle problems, such as a PASS recorded on an older commit or a missing mandatory check, given only the JSON.
- An activation arm: the skill installed but not named in the prompt.

## Metrics

| Metric | Status |
| --- | --- |
| Vulnerability detection rate | Measured on 2026-11-26. Both arms at ceiling |
| False-positive rate | Measured on 2026-11-26. Both arms 0 |
| Release decision accuracy | Measured on 2026-11-26. Both arms 6 / 6 |
| Token consumption | Measured on 2026-11-26 |
| Audit execution time | Measured on 2026-11-26 |
| Verified remediation rate | Not measured |
| Activation accuracy | Not measured |

Measure activation before claiming detection gains from an installed skill. A skill that is copied into a skills folder may never load for the task, and every other metric then compares two identical runs.

The script tests under `tests/` check the validators and the release gate. They are not a measure of how often an agent finds a vulnerability.

# Benchmarks

## 2026-11-26: harder cases

**Result: both arms passed all 72 graded checks again.** The model found every subtle defect and made no false positives, with or without the skill. The skill changed how the agent worked, not what it found, and in two cases it made the agent look less closely.

The 17 cases were built to fix the limits of the first run below:

- **7 defects that are not in the obvious file.** An admin route outside the middleware's matcher. A price looked up and then overwritten by the request body. A `SECURITY DEFINER` database function that skips row-level security. A Stripe webhook that grants access before a Bacs or bank-transfer payment clears. A wallet transfer that accepts a negative amount. An organisation ID taken from a request header. A URL allowlist that checks a string prefix.
- **4 pieces of secure code that look wrong.** An update policy with no `WITH CHECK`, which PostgreSQL covers with `USING`. A Prisma extension that scopes every read. Tagged-template SQL. A correct webhook.
- **6 audit cases, each a real Git repository.** The evidence for `ownership` is from an older commit. `payment-verification` is missing. A critical check passed on code reading alone. A high finding is marked accepted. Three critical checks "passed" with the commands `true` and `echo`. One audit is genuinely CONDITIONAL GO.

| | Without the skill | With the skill |
| --- | --- | --- |
| Runs | 3 | 3 |
| Graded checks passed | 72 / 72 | 72 / 72 |
| Defects detected | 21 / 21 | 21 / 21 |
| Severity within one level | 21 / 21 | 21 / 21 |
| False positives on secure code | 0 / 12 | 0 / 12 |
| Correct release decision | 18 / 18 | 18 / 18 |
| Mean tokens per run | 71,107 | 83,980 (+18%) |
| Mean tool calls per run | 8.0 | 9.7 |
| Mean time per run | 68.9 s | 76.9 s (+12%) |

### Observations outside the score

Counted by text match over the summaries after grading. They are reported, not scored.

| Behaviour | Without the skill | With the skill |
| --- | --- | --- |
| Names `release_gate.py` in an audit-case summary | 0 / 18 | 17 / 18 |
| Commands that test nothing: says the script prints GO and overrides it | 0 / 3 | 3 / 3 |
| `SECURITY DEFINER` case: notes that signed-out users can call the function too | 0 / 3 | 3 / 3 |
| Cites a CWE (out of 51 summaries) | 0 | 12 |
| Rates one of the 7 high defects as critical (out of 21) | 8 | 3 |
| Static-evidence case: notices the recorded claim does not match the code | 3 / 3 | 0 / 3 |
| Missing-check case: points to the test file that exists for the missing check | 3 / 3 | 0 / 3 |

Two results matter most:

- **The skill did not blindly trust its own gate.** On the forged audit, `release_gate.py` prints GO because every field is filled in. All three skill runs ran it, saw GO, and recorded NO-GO because the commands test nothing. Without the skill, the agent also reached NO-GO, by reading the file.
- **The skill made the agent stop at the gate's reason.** In the static-evidence case, the audit claims every query is scoped to the organisation, while the code scopes by `owner_id`. Every run without the skill noticed this, and no run with the skill did. Those runs reported the gate's reason, static evidence on a critical check, and went no further. The decision was right either way, but a reviewer would want the mismatch. The skill should say that the gate's NO-GO reasons are where to start, not the whole review.

### Method

The same as the first run, with these differences:

- **Cases:** built by [`evals/benchmark/hard_pack.py`](../evals/benchmark/hard_pack.py) with seed 20261127. Folders have neutral names in a shuffled order, comments that explain why a decoy is safe were removed, and audit repositories use fixed commit dates, so every build is identical. The answer key is written outside the pack.
- **Prompt:** the same as the first run, adjusted for 17 cases and Git repositories, and without the `check_status` and `full_audit` keys. See [`evals/benchmark/prompts.md`](../evals/benchmark/prompts.md).
- **Skill under test:** commit `4a2dee4`. The skill arm received `SKILL.md`, `references/`, `scripts/`, `schemas/`, `templates/`, and `docs/ci.md`.
- **Isolation:** the key and every copy of this repository were made unreadable during the runs.
- **Grading:** fixed rules in [`evals/benchmark/grade_hard.py`](../evals/benchmark/grade_hard.py). Raw answers, the key, cost per run, and scores are in `evals/benchmark/results/2026-11-26-hard/`.

### What this means

For this model, a strong frontier model, the cases still do not separate the arms on correctness. The skill's measured value is in process: it runs the gate, it records evidence, and it names standards. It costs about a fifth more tokens. The next useful runs are:

- A smaller, faster model, where detection may differ.
- Whole repositories with several defects and many files, where a checklist may stop the agent from skipping areas.
- An activation arm: the skill installed but not named in the prompt.

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

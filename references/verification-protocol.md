# Verification protocol

Use this protocol for every audit. Quick Scan, Full Audit, and Release Gate do not modify the application. Fix and Verify is the only mode that may change code, and only after the finding is recorded.

## Evidence classes

| Class | Meaning |
| --- | --- |
| Static | The control was read in source, configuration, or policy text |
| Runtime | The control was executed in a local or authorised environment |
| None | The check was not executed |

Reading an authorisation function is static evidence. It does not prove the function runs on the request that matters. Critical authorisation, tenant isolation, payment integrity, and database-policy checks require runtime evidence before they can PASS.

## Statuses

PASS, FAIL, NOT TESTED, BLOCKED, and NOT APPLICABLE.

PASS requires the command, exit code, expected result, and observed result. A file and line reference can support a static finding. It cannot by itself PASS a critical control.

## What to record for each executed test

- Test ID
- Git commit that was tested
- Environment: `local` or `authorised-staging`
- Command
- Exit code
- Expected result
- Observed result
- Timestamp
- Evidence location

Record the same commit in `docs/audits/audit-result.json`, and record the commit on every mandatory check that passed. Run `scripts/release_gate.py` with `--head` set to the current commit. Without `--head` it reads HEAD from the repository that holds the audit file and exits 2 when it cannot. If any commit differs from HEAD, or a PASS has no commit, the evidence is stale and the decision is NO-GO.

## What `audit-result.json` must contain

Schema version `1.1`. Start from `scripts/scaffold_audit.py`, which lists every check.

- **Every mandatory check.** The 25 IDs in `schemas/mandatory-checks.json` must each appear once. A missing or duplicated ID is NO-GO. A check marked critical there cannot be recorded as non-critical. App-specific checks may be added with new IDs.
- **A recorded run for every runtime PASS:** `commit` equal to HEAD, `command`, `exit_code` of `0`, `observed`, and `executed_at`. A static PASS, allowed only for non-critical checks, still needs `commit` and `observed`.
- **A justification for every NOT APPLICABLE**, in `justification`. For example: "The application takes no payments."
- **A verification run for every fixed critical or high finding**, with the same fields as a runtime PASS, on the current commit. A fix verified on an older commit is stale.
- **An approval record for every accepted risk** in `accepted_risks`: `id` of the accepted medium or low finding, `owner`, `approved_by`, `approved_at`, and `reason`. A record that matches no accepted finding is NO-GO.

The gate also runs `git status` in the repository that holds the audit file. Only the audit file and the six report files beside it (`application-audit.md`, `security-findings.md`, `threat-model.md`, `test-matrix.md`, `remediation-plan.md`, `production-readiness.md`) may be uncommitted. Any other changed or untracked file, including one in the audit folder, means the checks did not run against what would ship, and the decision is NO-GO until it is committed and the checks are re-run. If the audit file is not in a Git repository, or `git status` fails, the gate cannot confirm what would ship, and the decision is NO-GO.

### What the gate cannot prove

The gate checks that the evidence is complete, consistent, and recorded on the current commit. It cannot prove that a recorded command really ran, that its output was not edited, or that an approval came from the person named. An agent could write a convincing record without running anything. Two habits close most of that gap:

- Run the tests and the gate in CI on the release commit, so the passing run comes from CI and not from the audit file. `scripts/ci_evidence.py` and `templates/ci/guardian-release.yml` do this. With `--ci-evidence`, the gate accepts a runtime PASS only when CI ran the same command on the same commit, in the same workflow run, and it passed. See [docs/ci.md](../docs/ci.md).
- Add accepted risks in a pull request that the named approver reviews, so the approval is in the review history.

Committing the audit reports creates a new commit. Evidence recorded on the commit before stays current when the only files that changed since are the audit file and its report files, and that commit is an ancestor of HEAD. Any other change makes it stale.

## Finding labels

| Status | Use when |
| --- | --- |
| open | The defect was confirmed and is not fixed |
| suspected | The risk is plausible and has not been observed |
| fixed | A regression test failed before the change and passed after it |
| false_positive | The report was wrong. Say why |
| accepted | A medium or low risk has an owner and an explicit acceptance |

Do not accept a critical or high finding. A suspected critical or high finding stays NO-GO until it is confirmed and fixed, or reclassified with evidence.

## Release decision

Do not type GO, CONDITIONAL GO, or NO-GO from memory. Calculate it:

```bash
python scripts/release_gate.py docs/audits/audit-result.json --head "$(git rev-parse HEAD)"
```

The script is the decision. It returns exit 0 for GO and CONDITIONAL GO, and exit 1 for NO-GO.

| Condition | Decision |
| --- | --- |
| Unresolved critical or high finding | NO-GO |
| Critical or high finding marked accepted | NO-GO |
| Failed, blocked, or unexecuted mandatory check | NO-GO |
| Missing, duplicated, or downgraded mandatory check | NO-GO |
| NOT APPLICABLE without a justification | NO-GO |
| PASS without a recorded run (command, exit code 0, observed result, timestamp, commit) | NO-GO |
| Critical control with only static evidence | NO-GO |
| Fixed critical or high finding without a passing run on HEAD | NO-GO |
| Audit or check commit differs from HEAD, beyond committing the audit reports | NO-GO |
| With `--ci-evidence`: a recorded run that CI did not repeat, or that failed in CI | NO-GO |
| Uncommitted changes other than the audit reports | NO-GO |
| Working tree cannot be checked (not a Git repository, or `git status` failed) | NO-GO |
| Open medium or low finding without acceptance | NO-GO |
| Accepted risk without owner, approver, date, and reason | NO-GO |
| Accepted medium or low risk, and no blocker above | CONDITIONAL GO |
| Applicable mandatory checks passed and no open findings remain | GO |

A material change to a verified control invalidates that evidence. Re-run the test on the new commit.

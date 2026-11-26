# Changelog

## Unreleased

The version stays 0.4.0 until measured benchmarks exist.

- README hero keeps the shield, the drawn check, and the six-row cycle. The surface uses the Intellygent mark's green and gold, and a small mark stays in the corner. The image is embedded, so the banner still makes no external request.

- `release_gate.py`: `--head` now always replaces any `head_commit` written in the audit file. Before, a file that recorded its own HEAD could pass GO on a later commit.
- `release_gate.py`: a mandatory check that passed at a different commit is stale and returns NO-GO.
- `release_gate.py`: a critical or high finding marked `fixed` needs runtime evidence. A fix supported only by static reading returns NO-GO.
- Added regression tests for the three cases above. Each test fails on the previous gate code.
- `release_gate.py`: without `--head`, the gate reads HEAD from the Git repository that holds the audit file, and exits 2 when it cannot. Before, it compared the file only with itself and could print GO.
- `release_gate.py`: a PASS with no recorded commit is not fresh evidence and returns NO-GO.
- `detect_stack.py`: `pyproject.toml` is parsed as TOML and only declared dependencies count (PEP 621, dependency groups, Poetry). A framework named in a comment or description no longer matches.
- `SKILL.md`: check that `docs/audits/` is not ignored by Git, and treat a gate that could not run as NO-GO.
- Added four regression tests for the changes above. Each fails on the previous code.
- `references/security-testing.md`: named the SQL shapes that AI-generated code produces (string-built SQL, ORM escape hatches with interpolation, identifiers taken from the request, dynamic SQL in database functions, second-order input, NoSQL operators), their safe forms, and runtime checks that need no exploit payload.
- Added a matched pair of SQL evaluation fixtures: a string-built query with a request-controlled sort, and a bound query with an allowlisted sort that must not be reported.
- README rewritten around what the skill checks and how the release gate decides.
- README explains how a run works and why the skill exists, and groups the checks by area.
- `release_gate.py`: a failed `git status`, or an audit file outside a Git repository, is NO-GO. Before, both read as a clean working tree.
- `release_gate.py`: only the audit file and the six report files beside it may be uncommitted. Before, the whole folder holding the audit file was skipped, so an audit file saved next to code hid changes to that code.
- Added five regression tests for the two changes above. Each fails on the previous gate.
- `references/verification-protocol.md` and README: say what the gate cannot prove, and how CI and reviewed approvals close the gap.
- `release_gate.py`: committing the audit reports no longer makes the evidence stale. A recorded commit stays current when it is an ancestor of HEAD and only the audit file and report files changed since. Before, a committed audit could never pass.
- Added `scripts/ci_evidence.py`. In CI it re-runs every recorded runtime command without a shell, with a time limit, an allowlist of test runners, and no secrets in the environment, and writes the exit code and an output hash for each.
- `release_gate.py --ci-evidence`: a runtime PASS or a fixed critical or high finding needs a passing CI run of the same command, on the same commit, in the same workflow run, with the audit file unchanged since.
- Added `templates/ci/guardian-release.yml` (actions pinned to commit SHAs, read-only token, no `pull_request_target`) and `templates/ci/CODEOWNERS`, with setup and branch protection in `docs/ci.md`.
- Added `references/finding-verification.md`: before confirming a finding, look for the guard that would stop it, check the path is reachable, and test the denied and allowed cases. Findings gain an optional `challenge` field.
- Added 20 tests for the changes above. A recorded commit must be a commit ID; a name such as HEAD or a branch never counts as current.
- `references/legal-exposure.md`: notices that match the data flow, erasure, children, cancellation, tracking consent, name searches, client secrets, provider spend caps, and licenses. Figures are taken from the GDPR text, the COPPA Rule, ROSCA, and the FTC's GoodRx and Epic orders. The vacated 2024 Negative Option Rule is not the cancellation standard.
- `references/legal-exposure.md`: privacy-notice contents, a deletion request for people who cannot sign in, pre-contract price and the 14-day withdrawal right, business identity, email opt-out, cookie refusal, form consent, SDK load order, deceptive interfaces, fake reviews, and unsubstantiated claims. The FTC junk-fee rule is limited to tickets and short-term lodging. WCAG text alternatives, contrast, and keyboard operation are named in `references/accessibility.md`.
- `references/security-testing.md`: deleting an account does not revoke a JWT that the server accepts on signature and expiry alone. Short-lived access tokens, server-side refresh tokens, and a real revocation check for privileged routes follow RFC 7519, RFC 6749, RFC 9700, and the OWASP session and JWT guidance.
- `references/security-testing.md`: a login stored in one process is invisible to the second instance. Sticky sessions are not the store. Twelve-Factor and the Express `MemoryStore` warning are the sources. A long-lived JWT is not the substitute.
- Second benchmark, 17 harder cases: defects outside the obvious file, secure decoys, business-logic abuse, and audit evidence in real Git repositories. Both arms passed 72 of 72 checks; the skill added about 18% tokens. With the skill, the agent overrode the gate's GO when commands tested nothing, and it less often checked an audit's claims against the code. Pack builder, grader, and results are in `evals/benchmark/`.
- `release_gate.py`: a critical check, or a fixed critical or high finding, passes only with a command that starts a test runner and does not run inline code. `true`, `echo`, and `python -c` are NO-GO. `--allow-runner` adds a runner.
- `release_gate.py`: a critical check marked NOT APPLICABLE needs `approved_by`, at least one critical check must pass with a test, a critical or high false positive needs a `challenge`, and an accepted risk past `expires_at` is NO-GO.
- `release_gate.py`: `git status` and `git diff` run without rename detection and with submodules included, files marked skip-worktree or assume-unchanged count as changes, a recorded commit ID must resolve to a commit that starts with it, and `--head` must be the checked-out commit. Before, renaming code to a report name, a submodule bump, or a tag named like a commit ID could give GO. File names that are not valid UTF-8 no longer crash the gate.
- `release_gate.py --ci-evidence`: needs `GITHUB_RUN_ID`, checks the repository and run attempt, rejects exit codes that are not integers and checks recorded in more than one run.
- `ci_evidence.py`: restarts itself with a reduced environment on Linux and macOS, so commands cannot read secrets from the runner process; refuses inline code; keeps at most 5 MB of output while the command runs and records hashes of all output and of the kept log; stops leftover processes after each command; and does not hang when a child holds the output open.
- `templates/ci/guardian-release.yml`: tests and the gate run in separate jobs, so a test cannot edit the gate. The gate job runs even when the tests job fails. `templates/ci/CODEOWNERS` now protects the tests, their configuration, and dependency manifests by default. `docs/ci.md` describes the trust boundary.
- `detect_stack.py`: skips manifests that resolve outside the repository or are larger than 2 MB.
- `SKILL.md`: the gate's NO-GO reasons are where a review starts; compare recorded claims with the code.
- Hard benchmark pack: audit repositories now hold a small working app whose recorded tests pass when re-run, and the valid audit's NOT APPLICABLE check names an approver.
- Benchmark on Claude Haiku 5.5 and Claude Sonnet 5.5. Benchmark docs now say that agent isolation relied on instructions, not file permissions.
- Added 20 tests for the changes above. 19 fail on the previous code.
- Added `references/orchestration.md`: how every task starts. Pin down the request, mode, scope, commit, and what done means; collect context with read-only commands; tie every claim to a file or a command; plan each step with its check; keep a list of what was and was not reviewed; and stop and ask instead of guessing. `SKILL.md`, the audit report template, and the README point to it.
- Control registry: `guardian-checks.json` binds each mandatory check to named pytest tests and the exact command that runs them (`schemas/guardian-checks.schema.json`, `templates/ci/guardian-checks.json`). With `--controls`, `ci_evidence.py` adds `--junitxml`, removes any earlier report, and records every test's outcome. The gate returns NO-GO when the report is missing, no tests ran, or a required test did not run, failed, or was skipped. It also returns NO-GO when a critical PASS has no registry entry or uses another command, or when the registry is uncommitted or has no line in CODEOWNERS. Other runners stay unverified and never pass on their exit code.
- `release_gate.py` and `ci_evidence.py`: commands that only print version, help, or a test list (`pytest --version`, `go version`, `npm --version`) cannot prove a check. `python -m` must run pytest or unittest, and plain `python` must run a script.
- The CI template passes `--controls guardian-checks.json`, and the CODEOWNERS template lists the registry. `docs/ci.md` says a merge queue or required up-to-date branches, not a check inside the workflow, keeps the base current.
- Added 19 tests for the changes above, 6 of them end to end with real pytest reports. 12 fail when the new checks are switched off. The end-to-end tests are skipped where pytest is not installed.
- `docs/benchmarks.md`: measure activation before detection.
- Roadmap prompt: neutral, maintainer-facing wording.
- `release_gate.py`: every check in the new `schemas/mandatory-checks.json` (25 checks, matching the release checklist) must appear once in `audit-result.json`. A missing, duplicated, or downgraded critical check is NO-GO.
- `release_gate.py`: a runtime PASS needs a recorded run: command, exit code 0, observed result, timestamp, and the current commit. A static PASS, allowed only for non-critical checks, needs an observed result. NOT APPLICABLE needs a justification.
- `release_gate.py`: a fixed critical or high finding needs a passing run on the current commit, not only runtime evidence from any commit.
- `release_gate.py`: uncommitted or untracked files outside the audit folder are NO-GO, so checks always describe what would ship.
- `release_gate.py`: an accepted risk needs an owner, an approver, an approval date, and a reason, and must match an accepted medium or low finding.
- Audit schema version 1.1. `accepted_risks` holds approval records instead of IDs, and checks accept a `justification`. Files at version 1.0 are rejected with a clear error.
- `scaffold_audit.py` starts `audit-result.json` with all 25 mandatory checks as NOT TESTED. The release checklist shows each check's ID and whether it is critical.
- Sixteen new regression tests. The bypasses they cover returned GO or CONDITIONAL GO on the previous gate.
- First with-and-without benchmark: 3 runs per arm, 18 blind cases, mechanical grading. Both arms passed 96 of 96 checks; the skill added about 25% tokens and 64% time. Results, prompts, pack builder, and grader are in `evals/benchmark/`.
- Skills CLI install verified for Claude Code, Cursor, Codex, GitHub Copilot, and Gemini CLI locations. Loading inside each agent is recorded separately in `docs/compatibility.md`.
- README: animated header and release-gate terminal (self-hosted SVG, no external services, respects reduced motion), CI badges, and quick links.
- Added the v0.5 scenario-playbook upgrade prompt at `docs/roadmap/v0.5-upgrade-prompt.md`. It is a plan, not implemented work.

## 0.4.0

The original testing, security, privacy, payment, and AI scenarios are still in the reference files. This version makes the release decision depend on structured evidence.

- Added an evidence protocol that separates static inspection from runtime verification.
- Quick Scan, Full Audit, and Release Gate do not modify the application.
- Added `release_gate.py`, `validate_report.py`, `validate_skill.py`, and `detect_stack.py`.
- Added JSON schemas for an audit and a finding.
- Added explicit checks for fail-open defaults, tokens, cryptography, traversal, deserialisation, prototype pollution, GraphQL, WebSockets, caches, webhooks, mobile and PWA clients, MCP tools, supply chain, CI, email, SMS, jobs, feature flags, and DNS.
- Added short framework notes for Next.js, React, Supabase, Firebase, Stripe, Django, and FastAPI.
- Added synthetic evaluation fixtures. Agent detection rates are not measured.
- Added CI workflows that validate the skill and run the script tests. The release workflow packages source. It does not publish a GitHub release.
- Documented manual installation. `npx skills add` is not verified.

## 0.1.0

Initial public skill: operating modes, domain references, audit templates, and the scaffold script.

# Application audit

| Field | Value |
| --- | --- |
| Application | |
| Date | |
| Mode | Quick Scan / Full Audit / Fix and Verify / Release Gate |
| Auditor | Application Guardian |
| Environment | Local / authorised staging. Not production unless explicitly authorised. |
| Release recommendation | GO / CONDITIONAL GO / NO-GO |

## Executive summary

State the release recommendation and the few findings that decide it. Do not claim the application is free of vulnerabilities.

## Scope

In scope:

Out of scope:

Known, assumed, and not available:

## Architecture

Stack, trust boundaries, roles, data stores, auth, payments, storage, AI, and deployment. Describe only what was inspected.

## Methods

Static review, tests executed, and runtime checks. Name the commands and the environment.

## Test results

| Area | Status | Evidence |
| --- | --- | --- |
| Input validation | NOT TESTED | |
| Network failure | NOT TESTED | |
| Device and browser | NOT TESTED | |
| Accessibility | NOT TESTED | |
| Concurrency | NOT TESTED | |
| Account lifecycle | NOT TESTED | |
| Authentication | NOT TESTED | |
| Access control | NOT TESTED | |
| Admin privileges | NOT TESTED | |
| XSS and content | NOT TESTED | |
| Injection | NOT TESTED | |
| API | NOT TESTED | |
| Browser and HTTP | NOT TESTED | |
| SSRF and outbound requests | NOT TESTED | |
| Private data | NOT TESTED | |
| Files and uploads | NOT TESTED | |
| Secrets | NOT TESTED | |
| Privacy lifecycle | NOT TESTED | |
| Database policies | NOT TESTED | |
| Payments and entitlements | NOT TESTED | |
| AI | NOT TESTED | |
| Dependencies | NOT TESTED | |
| Deployment | NOT TESTED | |
| Rate limiting | NOT TESTED | |
| Logging | NOT TESTED | |
| Performance | NOT TESTED | |
| Resilience | NOT TESTED | |

Status values: PASS, FAIL, NOT TESTED, BLOCKED, NOT APPLICABLE.

PASS requires evidence. List tests not executed and why.

## Confirmed vulnerabilities

Summarise items from `security-findings.md` that were observed.

## Suspected vulnerabilities

Summarise items that still need investigation. Do not upgrade suspicion to confirmation.

## Release blockers

## Remediation priorities

1. Critical / P0
2. High / P1
3. Medium / P2
4. Low / P3

## Changes implemented

None, unless this run included Fix and Verify. For each change: finding ID, files, tests run, and result.

## Remaining risk

## External verification required

Actions that need infrastructure access, legal review, provider consoles, or explicit approval. Do not perform them in the audit.

## Finding schema

Use this schema in `security-findings.md` for every finding:

| Field | Value |
| --- | --- |
| ID | AG-001 |
| Title | |
| Severity | Critical P0 / High P1 / Medium P2 / Low P3 / Informational |
| Confidence | Confirmed / Suspected |
| Location | file:line |
| Component | |
| Description | |
| Root cause | |
| Preconditions | |
| Impact | |
| Expected | |
| Observed | |
| Safe reproduction | Synthetic data only. No secrets. |
| Evidence type | static / runtime / none |
| Commit | Git commit that was tested |
| Command | |
| Exit code | |
| Executed at | |
| Remediation | |
| Reference | OWASP / CWE |
| Regression test | |
| Verification | Not verified / Verified with evidence |

The release decision is the output of `scripts/release_gate.py` on `audit-result.json`. Do not write a decision that disagrees with that command.

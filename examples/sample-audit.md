# Sample audit: Harbor Notes

This is a fictional audit of a fictional note-taking service. The users, invoices, and commands are synthetic. It shows the shape of a report. It is not evidence about a real product, and it is not a measured benchmark.

| Field | Value |
| --- | --- |
| Application | Harbor Notes |
| Date | 2026-11-26 |
| Mode | Full Audit |
| Environment | local |
| Commit | example0001 |
| Release recommendation | NO-GO |

## Executive summary

Harbor Notes lets a signed-in user open another user's invoice by changing the id in the request. `scripts/release_gate.py` prints NO-GO for [sample-audit-result.json](sample-audit-result.json). The application is not approved for production.

## Scope

In scope: invoice reads and the release decision for commit `example0001`.

Out of scope: the payment provider, because this fixture has no payment code.

## Test results

| Area | Status | Evidence |
| --- | --- | --- |
| Invoice ownership | FAIL | Runtime. `pytest tests/test_invoices.py::test_other_user_cannot_read` exited 1. User A received HTTP 200 for User B's invoice. |
| Payments | NOT APPLICABLE | No payment code in this fixture. |
| Database policies | NOT TESTED | No database was available in the fixture. |

## Confirmed vulnerabilities

AG-001. See [sample-security-findings.md](sample-security-findings.md).

## Release blockers

The ownership check failed at runtime. A high finding is open. The script must print NO-GO.

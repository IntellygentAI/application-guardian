# Sample security findings

Fictional findings for Harbor Notes. No real customer data.

| ID | Title | Severity | Confidence | Verification |
| --- | --- | --- | --- | --- |
| AG-001 | Any signed-in user can read another user's invoice | high | confirmed | runtime, test failed |

## AG-001

| Field | Value |
| --- | --- |
| ID | AG-001 |
| Title | Any signed-in user can read another user's invoice |
| Severity | high |
| Confidence | confirmed |
| Evidence type | runtime |
| Location | app/api/invoices/[id]/route.ts:12 |
| Commit | example0001 |
| Command | pytest tests/test_invoices.py::test_other_user_cannot_read |
| Exit code | 1 |
| Expected | HTTP 404 or 403 and no invoice fields |
| Observed | HTTP 200 and the invoice total for the other synthetic user |
| Executed at | 2026-11-26T03:00:00Z |
| Remediation | Load the invoice for the authenticated user only. Re-run the same test. |

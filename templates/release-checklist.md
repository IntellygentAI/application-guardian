# Production release checklist

| Field | Value |
| --- | --- |
| Application | |
| Date | |
| Decision | GO / CONDITIONAL GO / NO-GO |

The decision field must match `scripts/release_gate.py`. A handwritten GO is not the decision.

Complete every row. PASS requires evidence. Do not leave a mandatory row blank.

| Check | Status | Evidence |
| --- | --- | --- |
| Authentication works securely | NOT TESTED | |
| Resource ownership is enforced | NOT TESTED | |
| Administrative operations are protected | NOT TESTED | |
| Tenant isolation is verified | NOT TESTED | |
| Database access policies are verified | NOT TESTED | |
| No known exposed production secrets remain | NOT TESTED | |
| Sensitive fields are not returned unnecessarily | NOT TESTED | |
| File storage permissions are correct | NOT TESTED | |
| Upload validation is effective | NOT TESTED | |
| Payment verification is secure | NOT TESTED | |
| Duplicate payments and redemptions are prevented | NOT TESTED | |
| Critical workflows have regression tests | NOT TESTED | |
| Account deletion behaves correctly | NOT TESTED | |
| Session invalidation works as intended | NOT TESTED | |
| Abuse-prone endpoints have appropriate protections | NOT TESTED | |
| Error messages do not expose internal information | NOT TESTED | |
| Security-relevant logging is available | NOT TESTED | |
| Dependency risks are assessed | NOT TESTED | |
| Critical accessibility problems are addressed | NOT TESTED | |
| Mobile and desktop layouts are usable | NOT TESTED | |
| Network failures are handled appropriately | NOT TESTED | |
| Backup and recovery are verified where applicable | NOT TESTED | |
| Production deployment configuration is reviewed | NOT TESTED | |
| AI integrations enforce independent permissions and usage limits | NOT TESTED | |
| Build, lint, type checks, and mandatory tests succeed | NOT TESTED | |

## Decision rule

- **GO.** Mandatory checks passed, and no unresolved release-blocking finding remains.
- **CONDITIONAL GO.** No unresolved critical or high-severity security finding remains. Lower-priority risks are listed for explicit acceptance.
- **NO-GO.** A critical or high-severity security issue, a failed mandatory test, an unverified critical control, or another release blocker remains.

## Accepted risks

Required for CONDITIONAL GO. Each row needs an owner.

| Risk | Severity | Owner | Acceptance note |
| --- | --- | --- | --- |
| | | | |

## Blockers

Required for NO-GO.

| Finding | Why it blocks release | Action required |
| --- | --- | --- |
| | | |

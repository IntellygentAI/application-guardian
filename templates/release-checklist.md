# Production release checklist

| Field | Value |
| --- | --- |
| Application | |
| Date | |
| Decision | GO / CONDITIONAL GO / NO-GO |

The decision field must match `scripts/release_gate.py`. A handwritten GO is not the decision.

Complete every row. The IDs match `schemas/mandatory-checks.json`, and `release_gate.py` requires each one in `audit-result.json`. PASS requires a recorded run on the current commit. NOT APPLICABLE requires a justification. A critical check cannot be marked non-critical.

| ID | Check | Critical | Status | Evidence |
| --- | --- | --- | --- | --- |
| `authentication` | Authentication works securely | yes | NOT TESTED | |
| `ownership` | Resource ownership is enforced | yes | NOT TESTED | |
| `admin-operations` | Administrative operations are protected | yes | NOT TESTED | |
| `tenant-isolation` | Tenant isolation is verified | yes | NOT TESTED | |
| `database-policies` | Database access policies are verified | yes | NOT TESTED | |
| `secrets` | No known exposed production secrets remain | yes | NOT TESTED | |
| `response-fields` | Sensitive fields are not returned unnecessarily | no | NOT TESTED | |
| `storage-permissions` | File storage permissions are correct | yes | NOT TESTED | |
| `upload-validation` | Upload validation is effective | no | NOT TESTED | |
| `payment-verification` | Payment verification is secure | yes | NOT TESTED | |
| `duplicate-prevention` | Duplicate payments and redemptions are prevented | yes | NOT TESTED | |
| `regression-tests` | Critical workflows have regression tests | no | NOT TESTED | |
| `account-deletion` | Account deletion behaves correctly | no | NOT TESTED | |
| `session-invalidation` | Session invalidation works as intended | no | NOT TESTED | |
| `abuse-protection` | Abuse-prone endpoints have appropriate protections | no | NOT TESTED | |
| `error-disclosure` | Error messages do not expose internal information | no | NOT TESTED | |
| `security-logging` | Security-relevant logging is available | no | NOT TESTED | |
| `dependency-risk` | Dependency risks are assessed | no | NOT TESTED | |
| `accessibility` | Critical accessibility problems are addressed | no | NOT TESTED | |
| `layouts` | Mobile and desktop layouts are usable | no | NOT TESTED | |
| `network-failures` | Network failures are handled appropriately | no | NOT TESTED | |
| `backup-recovery` | Backup and recovery are verified where applicable | no | NOT TESTED | |
| `deployment-config` | Production deployment configuration is reviewed | no | NOT TESTED | |
| `ai-permissions` | AI integrations enforce independent permissions and usage limits | yes | NOT TESTED | |
| `build-and-tests` | Build, lint, type checks, and mandatory tests succeed | no | NOT TESTED | |

## Decision rule

- **GO.** Mandatory checks passed, and no unresolved release-blocking finding remains.
- **CONDITIONAL GO.** No unresolved critical or high-severity security finding remains. Lower-priority risks are listed for explicit acceptance.
- **NO-GO.** A critical or high-severity security issue, a failed mandatory test, an unverified critical control, or another release blocker remains.

## Accepted risks

Required for CONDITIONAL GO. Only medium and low findings can be accepted. Each row needs an owner, an approver, an approval date, and a reason, and the same record goes in `accepted_risks` in `audit-result.json`.

| Finding | Severity | Owner | Approved by | Approved at | Reason |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Blockers

Required for NO-GO.

| Finding | Why it blocks release | Action required |
| --- | --- | --- |
| | | |

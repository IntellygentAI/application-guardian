# Data security and privacy

Review actual API response bodies, storage policies, and exports. The fields visible in the interface are not the full data surface.

## Private data exposure

Assume a caller will request data the interface does not show. Check whether an unauthorised caller can obtain email addresses, telephone numbers, home addresses, dates of birth, private profile fields, password hashes, authentication tokens, other users' invoices, private messages, uploaded documents, internal notes, financial information, organisation membership, or database backups.

Verify response allowlists, server-side field permissions, data minimisation, ownership, tenant isolation, export permissions, bounded pagination, rate limits, and access logging.

A password hash is a secret. Do not return it.

## Enumeration and scraping

Test empty search, excessive page size, walking a directory by pagination, search on private fields, sequential access to synthetic records, bulk export, unauthorised realtime subscriptions, and internal reporting endpoints.

Private records stay private. Search results respect permissions. Ordinary users cannot export sensitive directories. Bulk operations require the right privilege. Pagination and response size are bounded. Suspicious extraction can be detected where the product claims that control. Publicly searchable data is an explicit product decision.

Rate limiting is not a substitute for access control.

## File storage and downloads

Test, with synthetic objects:

- Another user's document, a private invoice, and a file belonging to another tenant
- An expired signed URL and listing of private objects
- Replacing or deleting another user's file
- Download without authentication, and access after permission revocation

Private files are not in an unrestricted public bucket. Public buckets contain only intentionally public content. Signed URLs are scoped and short-lived. Ownership is validated. Listing is restricted. Sensitive downloads are authorised. Caches do not bypass access control.

An unguessable file name is not access control.

## File upload

Test a non-image in a photo field, an extension that does not match the contents, an oversized file, an empty file, a corrupted image, an unsupported type, duplicates, unusual names, an interrupted upload, and active-content formats where only static images are expected.

Require an extension allowlist, content and format validation, size limits, safe filenames and storage paths, safe image processing, restricted executable content, malware scanning where the risk justifies it, metadata removal where required, safe download content types, ownership checks, and cleanup of abandoned uploads.

Do not trust the browser-supplied MIME type.

## Secrets and credential exposure

Scan the repository, build output, and configuration for accidental secrets. Inspect `.env`, `.env.local`, git history, frontend bundles, source maps, container images, CI logs, debug output, public directories, build artefacts, mobile packages, documentation, example config, error messages, and monitoring config.

Look for private API keys, database passwords, service-role credentials, Stripe secret keys, AI provider keys, OAuth client secrets, cloud credentials, webhook signing secrets, private signing keys, and hardcoded administrator passwords.

Secret files are excluded from version control. Sensitive values live in a secret manager. Server-only variables stay server-side. Public environment variables contain only intentionally public values. Build output does not embed private credentials.

If a real secret is exposed:

1. Report the location and the secret type. Do not reproduce the value.
2. Recommend immediate revocation and rotation.
3. Identify affected environments and dependencies.
4. In Fix and Verify mode, remove the insecure reference. In Quick Scan, Full Audit, and Release Gate, record the required change and do not edit the application.
5. Recommend reviewing repository history and access logs.
6. Verify that the replacement credential is not exposed.

Deleting a secret from the latest commit does not invalidate it or erase historical exposure. Do not rotate or revoke production credentials unless the user explicitly asks.

## Public files, backups, and debug artefacts

Inspect public directories and deployment config for database exports, SQL dumps, backup archives, environment files, git metadata, debug dashboards, server logs, internal documentation, temporary files, sensitive test fixtures, development-only routes, and unprotected administrative tools.

Production deploys only what is intended to be public.

## Privacy and data lifecycle

Verify that only necessary personal data is collected, sensitive data is protected in transit and at rest, personal data is kept out of unnecessary analytics, and logs omit passwords, tokens, and unnecessary personal information.

Account deletion revokes access. Deleted information follows the documented retention policy. Export is limited to authorised data. Backups follow retention and access policy. Shared devices do not show the previous user's cached private data. Third parties receive only the data they need.

Identify applicable privacy obligations, such as UK GDPR or EU GDPR, when the product context makes them relevant. Separate technical findings from matters that need legal or regulatory review. Do not give a legal conclusion. Notices, erasure, children, and tracking consent are in [legal-exposure.md](legal-exposure.md).

## Retention

Expired personal data, orphaned uploads, and backups are deleted or retained only for the documented period. Account deletion removes or irreversibly anonymises the private data the policy names, including files and search indexes. Say when a backup cannot be edited and record the remaining retention as a risk, not as a completed deletion.

## Observability

Analytics, session replay, and error trackers do not receive passwords, tokens, message bodies, or payment details. A session recording of an authenticated page is private data. Logs that include those fields are findings.

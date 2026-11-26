# Production readiness

Use the tools the repository already has. Do not install a scanner, browser driver, or load generator only to satisfy this skill. Bounded load tests run only against authorised environments.

## Dependencies and supply chain

Inspect package manifests, lockfiles, container base images, build tools, GitHub Actions or equivalent CI workflows, external scripts, SDKs, browser extensions where relevant, and third-party plugins.

Check known vulnerable dependencies, unsupported libraries, suspicious or typosquat packages, unnecessary dependencies, unpinned critical build dependencies, unsafe install scripts, untrusted external scripts, and excessive third-party permissions.

Use the ecosystem's existing audit command. Do not perform a blind major-version upgrade.

## Deployment and cloud

Inspect environment separation, production debug settings, cloud IAM, public database access, firewall and network restrictions, administrative interfaces, TLS, secret injection, CI/CD permissions, preview deployments, backup encryption, container permissions, infrastructure configuration, and monitoring.

Preview and staging must not expose production data or production credentials. Avoid wildcard permissions unless the configuration documents why a narrower permission cannot work.

If the deployment config is not in the repository, record those checks as NOT TESTED and name the missing artefact.

## Rate limiting and abuse resilience

Identify expensive operations: login, registration, password reset, OTP verification, search, upload, report generation, email, SMS, AI generation, export, and payment initiation.

Verify per-user and appropriate network-level limits, maximum request size, pagination limits, query timeouts, queue limits, concurrency limits, quotas, caching, backpressure, and graceful degradation.

## Logging, monitoring, and detection

Security-relevant events should be detectable: repeated authentication failures, suspicious account activity, privilege changes, administrative operations, unauthorised access attempts, large exports, payment discrepancies, coupon abuse, unusual AI usage, file validation failures, repeated API errors, and unexpected infrastructure cost.

Logs are not public. They exclude credentials and unnecessary personal data. Important operations have correlation identifiers. Critical conditions have alerts. Log access is restricted. Security-sensitive logs have the retention and integrity protection the product requires.

## Performance

Measure against the documented budget. Inspect load time, Largest Contentful Paint, Interaction to Next Paint, Cumulative Layout Shift, bundle size, images, query performance, API latency, memory, background jobs, and mobile performance.

Check N+1 queries, missing indexes, unbounded queries, unnecessary requests, excessive rendering, memory leaks, unnecessary polling, large blocking scripts, unoptimised images, and excessive client-side fetching.

Report measured numbers. Do not claim a performance result that was not measured.

## Error handling and resilience

Test failure of the database, payment provider, auth provider, email, SMS, storage, AI provider, background workers, expired external credentials, malformed third-party responses, and partial outages. Use fakes or an authorised environment.

Errors are graceful. Users get a useful message. Stack traces stay internal. Failed transactions do not corrupt data. Retries are safe. Critical workflows recover. Failed jobs can be investigated and retried. The application does not report success after a failure.

## Frontend state and navigation

Test refresh, deep links, back and forward, multiple tabs, account switching, logout in another tab, closing a modal, leaving a dirty form, refresh during checkout, and returning after inactivity.

Check stale state, cached permissions, lost form data, broken navigation, hydration errors, infinite loading, false success messages, and private information left behind after logout.

## Automated test layers

Build the smallest strategy that matches the risk, using the repository's tools:

1. Unit tests for isolated logic
2. Integration tests for collaborating services
3. API tests for contracts and permissions
4. Database tests for constraints and policies
5. End-to-end tests for critical workflows
6. Security regression tests
7. Accessibility tests
8. Visual regression tests where the product already uses them
9. Performance tests where a budget exists
10. Concurrency tests for money, inventory, redemption, and unique accounts
11. Recovery and failure-injection tests for critical workflows

Suitable tools, when already justified by the repository, include Playwright or Cypress, Vitest or Jest, Testing Library, pytest, pgTAP, the Firebase Emulator Suite, axe-core, Lighthouse, OWASP ZAP in an authorised environment, Semgrep, CodeQL, Gitleaks, Trivy, the ecosystem dependency auditor, and k6 for controlled load tests.

## Regression

Every confirmed defect gets a regression test where that is technically feasible.

1. Identify the defect.
2. Reproduce it with synthetic data.
3. Add a test that demonstrates the failure.
4. Fix the underlying issue.
5. Re-run that test.
6. Run the related tests.
7. Confirm the legitimate behaviour still works.
8. Document the change and the evidence.

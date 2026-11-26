# Application Guardian

A Cursor skill for testing, security, privacy, and production readiness.

It tells the agent to review an application the way a QA engineer, application-security engineer, database-security reviewer, and site-reliability engineer would. A successful build, a polished screen, or a happy-path test is not evidence that the application is safe to ship.

The skill is technology-independent. Supabase, Firebase, payment providers, and AI integrations are reviewed only when the repository actually uses them.

## Why this matters for AI-generated applications

These are the failures to look for when an AI coding agent wrote or changed the application.

- **Frontend-only security.** The admin control is hidden, and an ordinary user can still call the operation.
- **Incorrect database permissions.** Sign-in works, and any signed-in user can read another user's records because ownership policies are missing.
- **Exposed credentials.** A private AI API key, database credential, or service-role key is included in frontend JavaScript.
- **Unverified payments.** Premium features unlock after the checkout redirect, with no confirmed payment.
- **Exposed private documents.** Invoices, identity documents, and personal uploads sit in public storage.
- **Overprivileged AI agents.** The assistant can reach the whole database or privileged tools. Access has to stay limited to the current user's authorised resources.
- **Race conditions.** Simultaneous requests create duplicate rewards, orders, or charges.
- **False confidence from testing.** The suite passes because it only covers the successful path. It never tries another user, invalid input, or a failed dependency.

## How it fits into development

```mermaid
flowchart TD
    change([New feature or code change]) --> threat([Threat modelling])
    threat --> build([Secure implementation])
    build --> tests([Functional and security tests])
    tests --> audit([Application Guardian audit])
    audit --> gate{"All mandatory checks passed?"}
    gate -->|Yes| ship([Eligible for deployment])
    gate -->|No, fix and retest| build

    classDef ready fill:#166534,stroke:#22c55e,color:#ffffff
    class ship ready
    linkStyle 6 stroke:#dc2626,color:#dc2626
```

Yes means the release gate returned GO, or CONDITIONAL GO with the remaining risks explicitly accepted. No sends the change back through secure implementation, tests, and another audit. The skill does not declare an application free of vulnerabilities.

## Install

Cursor loads a skill from a directory named `application-guardian` that contains `SKILL.md`.

**Every project on this machine**

macOS and Linux:

```bash
git clone https://github.com/IntellygentAI/application-guardian.git ~/.cursor/skills/application-guardian
```

Windows PowerShell:

```powershell
git clone https://github.com/IntellygentAI/application-guardian.git "$env:USERPROFILE\.cursor\skills\application-guardian"
```

**One repository**

From that repository's root:

```bash
git clone https://github.com/IntellygentAI/application-guardian.git .cursor/skills/application-guardian
```

Open a new Agent chat after installing. Cursor reads the skill list when the chat starts.

## Use it

Name the skill and the mode:

| Request | What the agent does |
| --- | --- |
| `Run Application Guardian full audit` | Assess the open application |
| `Run Guardian quick scan` | Review the current change |
| `Run Guardian database security audit` | Check policies, grants, and tenant isolation |
| `Run Guardian payment audit` | Check prices, webhooks, coupons, and entitlements |
| `Run Guardian AI security audit` | Check prompts, tools, data isolation, and cost limits |
| `Run Guardian fix and verify` | Fix confirmed findings and add regression tests |
| `Run Guardian release gate` | Decide GO, CONDITIONAL GO, or NO-GO |

The skill also applies when you create or change a feature, API, authentication flow, permission, database table or policy, file upload, payment, or AI integration, when you install dependencies, review a pull request, fix a bug, or prepare a deployment.

A first assessment defaults to a full audit. Later changes default to a check of the diff and the domains it touches.

## Modes

| Mode | Purpose |
| --- | --- |
| Quick Scan | Obvious security and reliability problems in the recent change |
| Full Audit | Repository and application assessment across every applicable domain |
| Fix and Verify | Remediate confirmed findings and prove the fix with a regression test |
| Release Gate | Production-readiness decision |

The release decision is **GO**, **CONDITIONAL GO**, or **NO-GO**. The skill does not declare an application free of vulnerabilities.

## What an audit produces

In the application repository:

```text
docs/audits/
├── application-audit.md
├── security-findings.md
├── threat-model.md
├── test-matrix.md
├── remediation-plan.md
└── production-readiness.md
```

Create the empty files from the templates:

```bash
python path/to/application-guardian/scripts/scaffold_audit.py --out docs/audits
```

The script does not overwrite a file that already exists. A test is marked PASS only when the report cites evidence. Otherwise the status is FAIL, NOT TESTED, BLOCKED, or NOT APPLICABLE.

## Repository layout

```text
application-guardian/
├── SKILL.md
├── references/
│   ├── functional-testing.md
│   ├── security-testing.md
│   ├── data-privacy.md
│   ├── database-security.md
│   ├── api-security.md
│   ├── payment-security.md
│   ├── ai-security.md
│   ├── accessibility.md
│   └── production-readiness.md
├── templates/
│   ├── audit-report.md
│   ├── threat-model.md
│   ├── test-matrix.md
│   └── release-checklist.md
└── scripts/
    └── scaffold_audit.py
```

`SKILL.md` is the operating manual: when to run, the four modes, mandatory rules, the audit workflow, severity, and the release decision. Each reference is the checklist for one domain. The agent reads a reference only when that domain is in scope.

| Concern | Where it lives |
| --- | --- |
| Role, invocation, rules, workflow, severity, release decision | `SKILL.md` |
| Input, network, devices, concurrency, accounts, permissions, locale | `references/functional-testing.md` |
| WCAG 2.2 AA | `references/accessibility.md` |
| Authentication, access control, admin privileges, XSS, injection, browser, SSRF | `references/security-testing.md` |
| API inventory and abuse cases | `references/api-security.md` |
| Private data, enumeration, files, secrets, privacy lifecycle | `references/data-privacy.md` |
| Supabase, PostgreSQL, Firebase, integrity, backup | `references/database-security.md` |
| Price, payment, coupons, subscriptions | `references/payment-security.md` |
| Prompt injection, tenant isolation, AI cost | `references/ai-security.md` |
| Dependencies, cloud, rate limits, logging, performance, resilience, tests | `references/production-readiness.md` |
| Authorisation matrix | `templates/test-matrix.md` |
| Audit report and finding schema | `templates/audit-report.md` |
| Threat model | `templates/threat-model.md` |
| Release checklist | `templates/release-checklist.md` |

## Limits

Adversarial checks use synthetic accounts, fictional data, and a local or authorised staging environment.

The skill does not:

- attack production or a third-party system without explicit authorisation
- print secret values or private customer data in a report
- deploy, rotate production credentials, change live data, or run a destructive migration unless you explicitly approve that action
- treat a hidden button, an unpredictable ID, a checkout redirect, or a public client key as a security control

Security checks belong at the backend, database, and infrastructure boundary. Frontend validation is not enough.

## Standards

The checklists follow current guidance from:

- [OWASP ASVS](https://owasp.org/projects/asvs/)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP API Security](https://owasp.org/projects/api-security/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [OWASP GenAI Security](https://genai.owasp.org/)
- [CWE](https://cwe.mitre.org/)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/projects/ssdf)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [Supabase Security](https://supabase.com/docs/guides/security)
- [Stripe](https://docs.stripe.com/)
- [Firebase Security Rules](https://firebase.google.com/docs/rules)

Framework-specific advice is checked against the version in the repository being reviewed.

## License

[MIT](LICENSE). Copyright (c) 2026 IntellygentAI.

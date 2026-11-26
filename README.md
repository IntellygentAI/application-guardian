<div align="center">

<img src="docs/assets/hero.svg" alt="Application Guardian: an animated banner showing attacker actions such as changing the ID in a URL, and the result the skill requires, such as a 403 with ownership checked on the server" width="100%">

# Application Guardian

**Security and release checks for applications built with AI coding agents.**

[![validate](https://github.com/IntellygentAI/application-guardian/actions/workflows/validate.yml/badge.svg)](https://github.com/IntellygentAI/application-guardian/actions/workflows/validate.yml)
[![tests](https://github.com/IntellygentAI/application-guardian/actions/workflows/tests.yml/badge.svg)](https://github.com/IntellygentAI/application-guardian/actions/workflows/tests.yml)
[![version](https://img.shields.io/badge/version-0.4.0-34d399)](CHANGELOG.md)
[![Agent Skills](https://img.shields.io/badge/format-Agent%20Skills-0ea5e9)](https://agentskills.io/specification)
[![license](https://img.shields.io/badge/license-MIT-64748b)](LICENSE)

[Install](#install) · [Use it](#use-it) · [Release gate](#the-release-gate) · [Results](docs/benchmarks.md) · [Contributing](#contributing)

</div>

Application Guardian is an agent skill. Install it, and your coding agent reviews an application before release: who can read whose data, whether prices and payments are checked on the server, what happens when the network drops or a user taps twice, and whether secrets reach the browser. It writes the findings to `docs/audits/` and a script decides whether the release can go out.

It works with any stack. Supabase, Firebase, Stripe, Next.js, Django, and FastAPI get extra checks when the repository uses them.

## What it checks

- One user reading or changing another user's records, invoices, files, or messages
- Admin actions that are hidden in the interface but still callable
- Database policies that let any signed-in user read every row
- Secret keys in frontend code, built bundles, or Git history
- Prices, quantities, and payment status taken from the browser
- Premium access granted from a checkout redirect instead of a verified payment event
- Coupons, credits, and sign-ups that can be used twice by sending requests at the same time
- SQL built by joining strings, including sort columns taken from the request
- Private uploads in public storage
- AI tools that can reach data the current user cannot
- Lost connections, double taps, long input, other languages, time zones, denied permissions, and screen readers

The full list is in `references/`. Each file covers one area, and the agent reads it only when that area applies.

## The release gate

The agent does not decide whether to release. `scripts/release_gate.py` reads `docs/audits/audit-result.json` and prints GO, CONDITIONAL GO, or NO-GO.

<img src="docs/assets/release-gate.svg" alt="Animated terminal: release_gate.py on the sample audit prints NO-GO with two reasons and exits 1" width="100%">

It returns NO-GO when:

- a critical or high finding is open, or was marked fixed without a passing test on the current commit
- any of the [25 mandatory checks](schemas/mandatory-checks.json) is missing, failed, or not run
- a check passed without a recorded command, exit code, result, and commit
- a critical check passed on code review alone, without a test that ran
- the evidence was recorded on a different commit, or there are uncommitted changes
- an accepted risk has no owner and approver, or is high or critical

CONDITIONAL GO means only medium or low risks remain, and each was accepted by a named person. A GO written in a report does not count. Only the script's output does.

## Install

With the Skills CLI, from your project:

```bash
npx skills add IntellygentAI/application-guardian
```

This puts the skill in `.agents/skills/` for Cursor, Codex, GitHub Copilot, and Gemini CLI, and links it into `.claude/skills/` for Claude Code.

Or clone it into your agent's skills folder. For Cursor:

```bash
git clone https://github.com/IntellygentAI/application-guardian.git ~/.cursor/skills/application-guardian
```

More options are in [docs/installation.md](docs/installation.md). The scripts need Python 3.11 or newer and nothing else.

## Use it

Ask your agent:

| Request | What happens |
| --- | --- |
| `Run Guardian quick scan` | Checks the current change and the areas it touches |
| `Run Application Guardian full audit` | Checks the whole application |
| `Run Guardian database security audit` | Policies, grants, and tenant isolation |
| `Run Guardian payment audit` | Prices, webhooks, coupons, and entitlements |
| `Run Guardian AI security audit` | Prompts, tools, data access, and cost limits |
| `Run Guardian fix and verify` | Fixes confirmed findings and adds a test for each |
| `Run Guardian release gate` | Runs the gate and reports the decision |

Scans and audits only read the code. Only fix and verify changes it, and only after you ask.

The first run on a repository is a full audit. After that, the agent checks each change.

## What an audit produces

```text
docs/audits/
├── application-audit.md      summary, scope, and decision
├── security-findings.md      each finding with file, line, and fix
├── threat-model.md
├── test-matrix.md            who can do what, allowed and denied
├── remediation-plan.md
├── production-readiness.md   the 25 mandatory checks
└── audit-result.json         the evidence the gate reads
```

Create them yourself, and run the gate:

```bash
python path/to/application-guardian/scripts/scaffold_audit.py --out docs/audits
python path/to/application-guardian/scripts/release_gate.py docs/audits/audit-result.json
```

The scaffold never overwrites a file. The gate exits 0 for GO or CONDITIONAL GO and 1 for NO-GO, so it can block a CI job.

A worked example with fictional data is in [examples/sample-audit.md](examples/sample-audit.md).

## Results

On 2026-11-26 the skill was tested against the same agent without it, on 18 small cases, three runs each. Both found every defect. With the skill, the agent also said that reading code is not enough to pass a check, and it ran the gate on audit files. Without the skill, it did neither. The skill used about 25% more tokens. The cases, every answer, and the grading script are in [docs/benchmarks.md](docs/benchmarks.md).

## Limits

- Tests run only against local or authorised staging environments, with made-up accounts and data. The skill does not attack production or anyone else's system.
- It does not print secret values or customer data in reports.
- It does not deploy, rotate credentials, change live data, or run destructive migrations without your approval.
- A GO is not proof that the application has no vulnerabilities. It means the mandatory checks ran and passed on that commit.

## Repository layout

| Path | Contents |
| --- | --- |
| `SKILL.md` | What the agent reads first: modes, rules, and the audit steps |
| `references/` | Checks for each area and framework |
| `scripts/` | Release gate, report validator, stack detector, scaffold |
| `schemas/` | Audit format and the mandatory check list |
| `templates/` | Report templates |
| `evals/` | Test cases and benchmark results |
| `docs/` | Installation, compatibility, architecture, roadmap |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md). Report a security problem as described in [SECURITY.md](SECURITY.md). Changes are listed in [CHANGELOG.md](CHANGELOG.md).

## Standards

The checks draw on [OWASP ASVS](https://owasp.org/projects/asvs/), the [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/), [OWASP API Security](https://owasp.org/projects/api-security/), the [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/), [OWASP GenAI Security](https://genai.owasp.org/), [CWE](https://cwe.mitre.org/), the [NIST SSDF](https://csrc.nist.gov/projects/ssdf), and [WCAG 2.2](https://www.w3.org/TR/WCAG22/), plus the security documentation for [Supabase](https://supabase.com/docs/guides/security), [Stripe](https://docs.stripe.com/), and [Firebase](https://firebase.google.com/docs/rules).

## License

[MIT](LICENSE). Copyright (c) 2026 IntellygentAI.

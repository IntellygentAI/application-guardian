# Coverage matrix

This maps the original specification and the later additions to the files that hold them. It is a map of instructions, not evidence that an agent executed them.

| Specification | Where it lives |
| --- | --- |
| 1–3 Role, modes, operating rules | `SKILL.md` |
| 4–6 and 8–11 Functional behaviour | `references/functional-testing.md` |
| 7 Accessibility | `references/accessibility.md` |
| 12–16 and 18–19 Application security | `references/security-testing.md` |
| 17 API security | `references/api-security.md` |
| 20–21 and 24–28 Privacy and files | `references/data-privacy.md` |
| 22–23 and 40 Database security and recovery | `references/database-security.md` |
| 29–32 Payments and entitlements | `references/payment-security.md` |
| 33–35 AI security | `references/ai-security.md` |
| 36–39 and 41–46 Production, performance, tests | `references/production-readiness.md` |
| 45 Authorisation matrix | `templates/test-matrix.md` |
| 47–52 Audit workflow | `SKILL.md` |
| 48 Threat model | `references/threat-modelling.md` and `templates/threat-model.md` |
| 53–55 Reports and release gate | Templates, `schemas/`, `scripts/release_gate.py` |
| 56–57 Standards and final instruction | `SKILL.md` |

## Additions after the original specification

| Addition | Where it lives |
| --- | --- |
| Fail-open defaults, JWT, MFA, passkeys, cryptography, traversal, deserialisation, prototype pollution, permission races | `references/security-testing.md` |
| Webhooks, GraphQL, WebSockets, cache isolation | `references/api-security.md` |
| AI output handling | `references/ai-security.md` |
| MCP and agent delegation | `references/agent-mcp-security.md` |
| Supply chain, CI, email, SMS, jobs, feature flags, DNS | `references/supply-chain-security.md` |
| Mobile and PWA | `references/mobile-security.md` |
| Retention and observability privacy | `references/data-privacy.md` |
| Tenant switching and recovery objectives | `references/database-security.md` |
| Static versus runtime evidence, freshness, deterministic decision | `references/verification-protocol.md` |
| Framework notes | `references/framework-specific/` |
| Skill evaluation fixtures | `evals/` |

Original scenarios that remain in force include long input, airplane mode, rotation, font scaling, dark mode, duplicate signup, account lifecycle, Apple Hide My Email, IDOR, admin routes, XSS, injection, price and quantity tampering, unverified payment, coupon races, Supabase RLS, public buckets, password hashes, and empty search. Those checks were not removed when the new sections were added.

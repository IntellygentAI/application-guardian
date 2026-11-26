# Changelog

## 0.4.0

The original testing, security, privacy, payment, and AI scenarios are still in the reference files. This version makes the release decision depend on structured evidence.

- Added an evidence protocol that separates static inspection from runtime verification.
- Quick Scan, Full Audit, and Release Gate do not modify the application.
- Added `release_gate.py`, `validate_report.py`, `validate_skill.py`, and `detect_stack.py`.
- Added JSON schemas for an audit and a finding.
- Added explicit checks for fail-open defaults, tokens, cryptography, traversal, deserialisation, prototype pollution, GraphQL, WebSockets, caches, webhooks, mobile and PWA clients, MCP tools, supply chain, CI, email, SMS, jobs, feature flags, and DNS.
- Added short framework notes for Next.js, React, Supabase, Firebase, Stripe, Django, and FastAPI.
- Added synthetic evaluation fixtures. Agent detection rates are not measured.
- Added CI workflows that validate the skill and run the script tests. The release workflow packages source. It does not publish a GitHub release.
- Documented manual installation. `npx skills add` is not verified.

## 0.1.0

Initial public skill: operating modes, domain references, audit templates, and the scaffold script.

# Changelog

## Unreleased

The version stays 0.4.0 until measured benchmarks exist.

- `release_gate.py`: `--head` now always replaces any `head_commit` written in the audit file. Before, a file that recorded its own HEAD could pass GO on a later commit.
- `release_gate.py`: a mandatory check that passed at a different commit is stale and returns NO-GO.
- `release_gate.py`: a critical or high finding marked `fixed` needs runtime evidence. A fix supported only by static reading returns NO-GO.
- Added regression tests for the three cases above. Each test fails on the previous gate code.
- `release_gate.py`: without `--head`, the gate reads HEAD from the Git repository that holds the audit file, and exits 2 when it cannot. Before, it compared the file only with itself and could print GO.
- `release_gate.py`: a PASS with no recorded commit is not fresh evidence and returns NO-GO.
- `detect_stack.py`: `pyproject.toml` is parsed as TOML and only declared dependencies count (PEP 621, dependency groups, Poetry). A framework named in a comment or description no longer matches.
- `SKILL.md`: check that `docs/audits/` is not ignored by Git, and treat a gate that could not run as NO-GO.
- Reported by an external review of v0.4.0. Four regression tests added; each fails on the previous code.
- README: animated header and release-gate terminal (self-hosted SVG, no external services, respects reduced motion), CI badges, and quick links.
- Added the v0.5 scenario-playbook upgrade prompt at `docs/roadmap/v0.5-upgrade-prompt.md`. It is a plan, not implemented work.

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

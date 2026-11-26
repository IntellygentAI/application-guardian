# Agent compatibility

Each row says exactly what was tried. A row is not marked verified because the layout looks compatible.

## Install with the Skills CLI

Verified on 2026-11-26 with `npx skills add IntellygentAI/application-guardian -y -a claude-code -a cursor -a codex -a github-copilot -a gemini-cli` in an empty Git project on Linux:

- The CLI cloned the repository, found one skill, `application-guardian`, and read its description.
- It installed the skill to `.agents/skills/application-guardian`, which the CLI reports as the shared location for Cursor, Codex, GitHub Copilot, and Gemini CLI, and symlinked `.claude/skills/application-guardian` for Claude Code.
- It wrote `skills-lock.json` with the source commit and a content hash.
- From the installed copy, `scripts/validate_skill.py` passed and `scripts/scaffold_audit.py` created `docs/audits/`.

## Loading inside each agent

| Agent | Install | Skill loaded and followed | Notes |
| --- | --- | --- | --- |
| Claude agents | Skills CLI verified | Verified when the agent is pointed at `SKILL.md` | In the [2026-11-26 benchmark](benchmarks.md), every skill-arm run read `SKILL.md`, used the references, and ran `release_gate.py`. Automatic activation from a description match was not measured. |
| Cursor | Skills CLI verified | Not verified | |
| Codex | Skills CLI verified | Not verified | |
| GitHub Copilot | Skills CLI verified | Not verified | |
| Gemini CLI | Skills CLI verified | Not verified | |
| Windsurf | Not tried | Not verified | |
| Antigravity | Not tried | Not verified | |
| OpenCode | Not tried | Not verified | |

"Install verified" means the files were placed where the CLI says the agent reads skills. It does not prove that the agent selects the skill for a task. Activation is a separate measurement: see [benchmarks.md](benchmarks.md).

The skill follows the [Agent Skills specification](https://agentskills.io/specification): `name`, `description`, optional `license`, `compatibility`, and `metadata`, plus `references/`, `scripts/`, and templates.

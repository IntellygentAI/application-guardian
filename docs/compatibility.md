# Agent compatibility

Compatibility is recorded only after an install and a successful skill load. This file does not claim support that has not been tried.

| Agent | Status | Notes |
| --- | --- | --- |
| Cursor | Documented manual install | Copy the repository into `.cursor/skills` or the user skills directory. An automated load test was not run in CI. |
| Claude Code | Not verified | |
| Codex | Not verified | |
| GitHub Copilot | Not verified | |
| Windsurf | Not verified | |
| Gemini CLI | Not verified | |
| Antigravity | Not verified | |
| OpenCode | Not verified | |
| `npx skills add IntellygentAI/application-guardian` | Not verified | The command matches the Skills CLI convention and was not executed here. |

The skill follows the [Agent Skills specification](https://agentskills.io/specification): `name`, `description`, optional `license`, `compatibility`, and `metadata`, plus `references/`, `scripts/`, and templates.

Update this table only after a real install. Do not change a row to verified because the layout looks compatible.

# Installation

Application Guardian is an [Agent Skills](https://agentskills.io/specification) directory. The required file is `SKILL.md` in a folder named `application-guardian`.

## Manual install

This is the documented method. It copies the skill into the location Cursor reads.

Every project on this machine, macOS and Linux:

```bash
git clone https://github.com/IntellygentAI/application-guardian.git ~/.cursor/skills/application-guardian
```

Windows PowerShell:

```powershell
git clone https://github.com/IntellygentAI/application-guardian.git "$env:USERPROFILE\.cursor\skills\application-guardian"
```

One repository, from that repository's root:

```bash
git clone https://github.com/IntellygentAI/application-guardian.git .cursor/skills/application-guardian
```

Open a new agent chat after cloning.

Other agents that load a `SKILL.md` directory can use the same folder. See [compatibility.md](compatibility.md) for what has and has not been verified.

## Skills CLI

Install with the Skills CLI:

```bash
npx skills add IntellygentAI/application-guardian
```

Global install:

```bash
npx skills add IntellygentAI/application-guardian -g
```

The project install was run against this repository on 2026-11-26: it placed the skill in `.agents/skills/application-guardian`, linked `.claude/skills/application-guardian`, and wrote `skills-lock.json`. The global install (`-g`) was not run. The manual copy above remains the fallback. See [compatibility.md](compatibility.md) for what each agent row means.

## Scripts

The audit scripts need Python 3.11 or newer and no third-party packages:

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

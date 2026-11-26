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

The Vercel Skills CLI convention for this repository is:

```bash
npx skills add IntellygentAI/application-guardian
```

Global install:

```bash
npx skills add IntellygentAI/application-guardian -g
```

These commands were not executed against this repository. Do not treat them as a verified installation method until that run succeeds. The manual copy above remains the fallback.

## Scripts

The audit scripts need Python 3.11 or newer and no third-party packages:

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

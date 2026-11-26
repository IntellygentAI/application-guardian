# Contributing

Application Guardian is MIT licensed. See [LICENSE](LICENSE).

## Develop

Python 3.11 or newer. No third-party packages.

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```

## Add a check

Put a new domain in `references/` and link it from `SKILL.md`. Keep `SKILL.md` under 500 lines. Do not copy the same checklist into a second file.

Framework notes belong in `references/framework-specific/` and should point at the domain reference instead of repeating it.

## Evidence

Do not write a GO in documentation unless `scripts/release_gate.py` prints GO for a real `audit-result.json`. Do not fill [docs/benchmarks.md](docs/benchmarks.md) with numbers that an agent run did not produce.

Synthetic fixtures live in `evals/fixtures/`. They are not real applications and they must not contain live credentials.

## Licences of other projects

Do not copy text or code from repositories whose licence is incompatible with MIT. Trail of Bits skills are CC BY-SA 4.0. Learn from the architecture. Do not paste their material into this repository.

## Pull requests

Describe the behaviour you changed and the tests you ran. The pull request template lists the checks.

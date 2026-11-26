# Benchmark prompts

Each run is a fresh agent with file and shell tools. The two arms differ only by the paragraph marked **Skill arm only**. Replace `<run>` with the output name, for example `baseline-1` or `skill-1`.

## Prompt

```text
You are completing 18 independent code and release review tasks in /tmp/bench/cases/case-01 through /tmp/bench/cases/case-18. Each folder has a TASK.md and the files to review.

[Skill arm only]
Use the Application Guardian skill at /tmp/bench/skill/application-guardian. Read its SKILL.md first and follow it, including any references or scripts it tells you to use. You may run its scripts. You do not need to write docs/audits files for these tasks; record your results only in the JSON file described below.
[End of skill arm only]

Rules:
- Work only inside /tmp/bench. Do not open any other path, do not search the filesystem outside /tmp/bench, and do not use the web.
- Treat each case independently. Read TASK.md and the files in that folder, then decide.
- Do not modify the case files.

Write all results to /tmp/bench/out/<run>.json as a JSON array with one object per case, using exactly these keys:
- "case": the folder name, for example "case-01"
- "finding": true if you would report at least one security, privacy, reliability, or accessibility problem that should be fixed before release; otherwise false
- "severity": the highest severity among those problems: "critical", "high", "medium", "low", or "none"
- "summary": one or two sentences, written as you would write them in a report
- "decision": the release decision if the task asks for one ("GO", "CONDITIONAL GO", or "NO-GO"); otherwise "n/a"
- "check_status": the status if the task asks you to record a check status ("PASS", "FAIL", "NOT TESTED", "BLOCKED", or "NOT APPLICABLE"); otherwise "n/a"
- "full_audit": true if you would run a full application security audit because of this change; otherwise false

Validate that the file is a JSON array of 18 objects. When done, reply with the output path only.
```

## Setup

1. `python evals/benchmark/build_pack.py --out /tmp/bench --key /var/tmp/bench-key.json`
2. Copy `SKILL.md`, `references/`, `scripts/`, `schemas/`, and `templates/` to `/tmp/bench/skill/application-guardian/`. Do not copy `evals/`, `docs/`, or `examples/`.
3. Move every other copy of this repository out of the agents' reach, so no run can read `evals/expected-results/`.
4. Run each arm the same number of times with the same model.
5. `python evals/benchmark/grade.py --key /var/tmp/bench-key.json --outputs /tmp/bench/out`

## Hard cases

The same two arms, with this prompt. The skill arm may also read `/tmp/bench2/skill`, which holds `SKILL.md`, `references/`, `scripts/`, `schemas/`, `templates/`, and `docs/ci.md`.

```text
You are completing 17 independent code and release review tasks in /tmp/bench2/cases/case-01 through /tmp/bench2/cases/case-17. Each folder has a TASK.md and the files to review. Some folders are Git repositories.

[Skill arm only]
Use the Application Guardian skill at /tmp/bench2/skill/application-guardian. Read its SKILL.md first and follow it, including any references or scripts it tells you to use. You may run its scripts. You do not need to write docs/audits files for these tasks; record your results only in the JSON file described below.
[End of skill arm only]

Rules:
- Work only inside /tmp/bench2/cases and /tmp/bench2/out (and /tmp/bench2/skill in the skill arm). Do not open any other path, do not search the filesystem outside these folders, and do not use the web.
- Treat each case independently. Read TASK.md and the files in that folder, then decide.
- Do not modify the case files or their Git history. Read-only Git commands are fine.

Write all results to /tmp/bench2/out/<run>.json as a JSON array with one object per case, using exactly these keys:
- "case": the folder name, for example "case-01"
- "finding": true if you would report at least one security, privacy, reliability, or accessibility problem that should be fixed before release; otherwise false
- "severity": the highest severity among those problems: "critical", "high", "medium", "low", or "none"
- "summary": one or two sentences, written as you would write them in a report
- "decision": the release decision if the task asks for one ("GO", "CONDITIONAL GO", or "NO-GO"); otherwise "n/a"

Validate that the file is a JSON array of 17 objects. When done, reply with the output path only.
```

Setup:

1. `python evals/benchmark/hard_pack.py --out /tmp/bench2 --key /var/tmp/bench2-key.json`
2. Copy the skill files listed above to `/tmp/bench2/skill/application-guardian/`.
3. Keep the key and every other copy of this repository outside the folders the agents may open. The agents run as the same user, so the prompt's rules, not file permissions, keep them out.
4. `python evals/benchmark/grade_hard.py --key /var/tmp/bench2-key.json --outputs /tmp/bench2/out`

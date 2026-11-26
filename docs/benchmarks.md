# Benchmarks

These metrics are defined so they can be measured later. No agent run produced them. Do not cite them as results.

| Metric | Result |
| --- | --- |
| Vulnerability detection rate | Not measured |
| False-positive rate | Not measured |
| Verified remediation rate | Not measured |
| Release decision accuracy | Not measured |
| Activation accuracy | Not measured |
| Token consumption | Not measured |
| Audit execution time | Not measured |

A future measurement compares the same model, environment, and task with and without this skill. The cases and the expected findings are in [../evals/evals.json](../evals/evals.json). `agent_result` is null until that run exists.

Measure activation first. A skill that is copied into a skills folder may never load for the task, and every other metric then compares two identical runs. Record, for each case, whether the agent read `SKILL.md` before answering. Report detection results only from runs where it did, and report the activation rate next to them.

The script tests under `tests/` check the validators and the release gate. They are not a measure of how often an agent finds a vulnerability.

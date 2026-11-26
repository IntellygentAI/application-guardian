# Orchestration: starting a task

Read this before the first finding, every time. Most wrong audits go wrong in the first few minutes: the agent guesses the task, guesses the stack, and then reasons from code it never opened. This file sets the order of work so that every claim rests on something you looked at or ran.

The rule behind every step: **if you did not open it or run it, you do not know it.** Say "not checked" instead.

## 1. Pin down the task

Write these five lines before you touch anything else. Put them at the top of your notes and, at the end, in the report's Scope section.

| Line | What to write | Where it comes from |
| --- | --- | --- |
| Request | The user's request, in one sentence, in their words | The message |
| Mode | Quick Scan, Full Audit, Fix and Verify, or Release Gate | The selection rules in `SKILL.md` |
| Scope | The diff, the paths, or the whole repository | The request, or `git diff` for a change |
| Commit | The full commit ID under review | `git rev-parse HEAD` |
| Done when | What the user gets at the end | The mode: findings, fixes with tests, or the gate's output |

If the request has more than one reasonable reading, write each one down. Pick one only when the selection rules in `SKILL.md` decide it. Otherwise ask, and say what each reading would lead to. Always ask before Fix and Verify if the user has not clearly asked for changes, because that mode edits code.

If the request conflicts with the repository, say so and stop. For example, the user asks for a payment audit and there is no payment code, or asks about a branch that does not exist. Do not pick a different task.

## 2. Collect context before reasoning

These commands are read-only. Run them, keep the output, and build the picture from it, not from what a typical app of this kind would have.

```bash
git rev-parse HEAD
git status --porcelain
git log --oneline -10
python <skill>/scripts/detect_stack.py .
```

Then find, by listing and opening files:

- **Entry points.** Every route, API handler, server action, RPC function, webhook, job, and CLI command. List the files you found them in.
- **Trust boundaries.** Where a request crosses from a user, a tenant, a partner, or the internet into code that holds data or money.
- **Data stores and policies.** Database migrations, row-level security, storage rules, and where the client key and the server key live.
- **Tests.** The test runner, the test command, and whether the tests run here. If they do not run, record why. That is a BLOCKED, not a PASS.
- **Prior evidence.** An existing `docs/audits/audit-result.json` and its commit. Run the gate on it before trusting anything it says.
- **Versions.** The framework and library versions in the lockfile. Framework behaviour depends on the version. Check the version before you rely on a default.

Record each fact with its source: a file and line, or a command and its output. Sort what you have into three lists, as the report's Scope section asks:

- **Known:** opened or run, with the source.
- **Assumed:** believed but not checked. Each assumption names the check that would confirm it.
- **Not available:** cannot be reached here, such as production, a third-party dashboard, or secrets. These become BLOCKED or NOT TESTED, never PASS.

## 3. Ground every claim

- Name a file, function, route, table, or setting only after you have opened it. Do not write `src/auth.ts` because apps like this usually have one.
- Quote the line you rely on, or give its file and line number.
- Do not describe what a command would print. Run it, or say it was not run.
- Do not fill a gap with a typical answer. An unknown stays unknown and is written down as unknown.
- When two sources disagree, for example a comment and the code, or the audit file and the code, the code that runs wins. Report the mismatch.
- When you are unsure, say what would settle it and do that, or record it as an open question.

## 4. Plan with a check for each step

Write a short plan before assessing. Pair every step with the check that proves it was done. Without a check, a step is a hope.

```text
1. List entry points          -> check: every route file in the tree is named, or excluded with a reason
2. Pick references            -> check: each reference is read or marked NOT APPLICABLE with a reason
3. Test ownership on invoices -> check: other-user read returns 404, own read returns 200, both commands recorded
4. Run the gate               -> check: its output is pasted unedited
```

Choose references from evidence. Read the framework file for each stack `detect_stack.py` printed, and each domain reference for a trust boundary you found in step 2. Mark the rest NOT APPLICABLE with a reason a reviewer can check, such as "no payment code: no Stripe or payment dependency, and no checkout route".

## 5. Keep a coverage list

As you work, keep a list of the areas and files you reviewed, and of those you did not. At the end, put it in the report's Methods section.

| Area or path | Reviewed | How | Not reviewed, and why |
| --- | --- | --- | --- |
| `app/api/invoices/` | Yes | Read handlers, ran ownership test | |
| `app/api/admin/` | Partly | Read middleware matcher | Handlers not opened: time limit |
| `supabase/migrations/` | No | | Stated as a gap |

An empty "not reviewed" column on a large repository is a warning sign, not a success. Saying what was skipped is how a reviewer knows where the audit stops.

## 6. From suspicion to finding

A pattern that looks wrong is a hypothesis, not a finding. Take each one through [finding-verification.md](finding-verification.md):

1. State the claim: who can do what, to which data, through which entry point.
2. Look for the guard that would stop it, in every layer the request passes.
3. Check that the path is reachable.
4. Test the denied case and the allowed case.

Only then record it as confirmed. A hypothesis you could not test stays `suspected`.

## 7. Keep changes narrow

This applies only in Fix and Verify.

- Every changed line traces to a confirmed finding.
- Do not reformat, rename, or refactor code the finding does not need. Match the existing style.
- An unrelated problem you notice is a new finding to record, not something to fix in the same change.
- Remove only what your own change made unused.
- Write the test that fails before the fix, then make it pass. The test is the proof, not the diff.

## 8. Stop and ask

Stop and ask the user instead of guessing when:

- the next step would change code, data, or configuration and the mode does not allow it
- the step needs production, real customer data, a real payment, or a third-party system
- a test needs a dependency or a service that is not installed
- two readings of the request lead to different work and the cost of the wrong one is high
- the repository contradicts the request

Record what you were about to do and why you stopped. A clear BLOCKED is a correct result.

## 9. Finish

The final answer says, in this order:

1. The task as pinned down in step 1.
2. What was reviewed and what was not, from step 5.
3. Findings, each with its evidence and challenge.
4. Commands that were run, and any that could not be run.
5. For a release decision, the gate's output, unedited.

Do not round up. "Not tested" stays "not tested" in the summary, even when everything else passed.

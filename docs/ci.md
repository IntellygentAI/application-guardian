# Running the release gate in CI

On its own, the gate checks that the evidence in `audit-result.json` is complete and recorded on the current commit. It cannot tell whether a command really ran. In CI it can: the workflow re-runs every recorded command itself, writes down what happened, and the gate accepts a PASS only if CI saw that command pass on that commit.

CI is only as trustworthy as the files it runs. Someone who can change the workflow, the tests, or the gate can make CI report success. The setup below makes each of those changes need approval from a named reviewer.

## What the workflow does

The workflow has two jobs, each on a fresh GitHub-hosted runner.

**`guardian-tests`**

1. Checks out the exact commit: the branch tip for a pull request, or the pushed commit.
2. Installs your application's test dependencies.
3. Runs `scripts/ci_evidence.py`. For every runtime PASS and every fixed critical or high finding, it runs the recorded command and records the exit code, start and finish times, the number of bytes printed, a SHA-256 hash of all output, and a hash of the log it kept.
4. Uploads the evidence and logs as a workflow artifact, kept for 90 days.

**`guardian-release`**, the required check

1. Checks out the same commit again on a new runner, so nothing the tests did can change the gate's files.
2. Downloads the evidence.
3. Runs `scripts/release_gate.py` with `--ci-evidence`. Besides its usual rules, the gate returns NO-GO when:
   - CI has no run of a recorded command, ran a different command, refused it, or saw it fail or time out
   - the evidence was produced on another commit, in another workflow run or attempt, or for another repository
   - the audit file changed after CI ran the commands
   - the same check appears in more than one run

This job runs even when the tests job fails, because GitHub treats a skipped required check as passing.

How commands run:

- Without a shell, from the repository root, with a time limit (15 minutes by default).
- The first word must be a known test runner, such as `pytest`, `npm`, or `go`. Add others with `--allow` here and `--allow-runner` on the gate. Inline code, such as `python -c` or `node -e`, is refused.
- With only basic environment variables such as `PATH` and `HOME`. On Linux and macOS, the runner restarts itself with that reduced environment before running anything, so a command cannot read secrets from its parent process either.
- At most 5 MB of output is kept per command. The rest is hashed, then dropped.
- When a command exits, anything it started in its process group is stopped.

## Trust boundary

This is not a sandbox. The recorded commands are your tests, and they run with the same rights as any other step in the tests job. The setup relies on three things:

- **Review.** The workflow, the skill, the audit file, the tests, and the dependency manifests change only through pull requests a code owner approves. `templates/ci/CODEOWNERS` lists them.
- **Separate jobs.** The gate runs on a different runner from the tests, so a test cannot edit the gate or the checkout it reads.
- **No secrets in the tests job.** Do not add `secrets.*` or deployment credentials to it. The workflow's token is read-only and checkout does not keep it.

What it does not stop:

- A test that starts a process in a new session (`setsid`) can outlive its command and change files, including the evidence, before upload. Only reviewed test code should run here.
- On Windows runners, the runner cannot drop its own environment, so keep secrets out of the job.
- A nested Git repository holding the audit file is checked as its own repository. Keep the audit in the application repository.
- Locally, `.git/info/exclude` and global ignore files can hide new files from `git status`. A fresh CI checkout has none.

## Set it up

1. Commit the skill to your repository. `npx skills add IntellygentAI/application-guardian` puts it in `.agents/skills/application-guardian/`. If you put it somewhere else, change `GUARDIAN` in the workflow.
2. Copy `templates/ci/guardian-release.yml` to `.github/workflows/guardian-release.yml`.
3. Replace the install step with your own, for example `npm ci`. It fails until you do.
4. Copy `templates/ci/CODEOWNERS` to `.github/CODEOWNERS` and name your release reviewers.
5. Make sure files your tests create, such as `node_modules/`, `.pytest_cache/`, or coverage output, are in `.gitignore`. The gate treats any other new file as an uncommitted change and returns NO-GO.
6. Commit the audit. Evidence recorded on the commit before the reports were added stays current, as long as only the audit file and the report files changed after it.
7. Turn on the branch protection settings below.

## Branch protection

In **Settings > Rules > Rulesets** (or **Branches > Branch protection rules**) for your default branch:

| Setting | Why |
| --- | --- |
| Require a pull request before merging | Every change goes through review |
| Required approvals: at least 1 | Someone other than the author looks at it |
| Require review from Code Owners | Changes to the workflow, the skill, and the audit file need a release reviewer |
| Dismiss stale approvals when new commits are pushed | An approval covers the code that was approved |
| Require approval of the most recent push | The author cannot approve their own last change |
| Require status checks to pass: `guardian-release` | The gate must pass before merging. Do not make `guardian-tests` the required check: the gate is the decision |
| Require branches to be up to date before merging | The gate ran on the code that merges |
| Block force pushes and deletions | History, and so the audited commit, cannot be rewritten |
| Bypass list: empty | Admins follow the same rules |

In **Settings > Actions > General**:

- Set **Workflow permissions** to read repository contents only.
- For pull requests from forks, require approval before workflows run.

## What this protects against, and what it does not

It stops:

- An agent or contributor writing PASS for a test that was never run, or that fails
- A PASS whose command tests nothing, such as `true`, `echo`, or `python -c pass`
- Evidence copied from an earlier run, attempt, commit, or repository
- A changed audit file slipping in after the tests ran
- A test editing the gate before it runs
- Secrets in the job's environment reaching the recorded commands, directly or through the runner process

It does not stop:

- **A pull request that changes the workflow, the tests, or the gate.** On `pull_request`, GitHub runs the workflow as it is in that branch, so such a PR can turn its own check green. Code-owner review is what catches it. A green `guardian-release` check on a PR that touches protected paths means nothing until a code owner approves it.
- **A reviewer who approves without reading.** The setup makes approval necessary, not careful.
- **Weak tests.** CI proves that the recorded command passed. It does not prove the command tests the right thing. That is what the audit and the review are for.
- **Self-hosted runners shared with untrusted code.** Use GitHub-hosted runners for public repositories.

## Following the security guidance

The workflow follows GitHub's guidance on [secure use of GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use):

- Every action is pinned to a full commit SHA, with the version in a comment. Turn on Dependabot for `github-actions` to keep the pins current.
- The token is read-only (`permissions: contents: read`), and checkout does not keep it (`persist-credentials: false`).
- It uses `pull_request`, never `pull_request_target`, so pull request code never runs with secrets or a write token.
- No `${{ }}` expression is placed inside a `run` script. Values reach scripts through environment variables.
- `CODEOWNERS` covers `.github/workflows/`.

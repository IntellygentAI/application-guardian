# Running the release gate in CI

On its own, the gate checks that the evidence in `audit-result.json` is complete and recorded on the current commit. It cannot tell whether a command really ran. In CI it can: the workflow re-runs every recorded command itself, writes down what happened, and the gate accepts a PASS only if CI saw that command pass on that commit.

CI is only as trustworthy as the files it runs. Someone who can change the workflow, the tests, or the gate can make CI report success. The setup below makes each of those changes need approval from a named reviewer.

## What the workflow does

1. Checks out the exact commit: the branch tip for a pull request, or the pushed commit.
2. Installs your application's test dependencies.
3. Runs `scripts/ci_evidence.py`. For every runtime PASS and every fixed critical or high finding, it runs the recorded command and records the exit code, start and finish times, and a SHA-256 hash of the output. It writes `ci-evidence.json` outside the repository.
4. Runs `scripts/release_gate.py` with `--ci-evidence`. Besides its usual rules, the gate returns NO-GO when:
   - CI has no run of a recorded command, ran a different command, refused it, or saw it fail or time out
   - the evidence was produced on another commit or in another workflow run
   - the audit file changed after CI ran the commands
5. Uploads the evidence and logs as a workflow artifact, kept for 90 days.

Commands run without a shell, from the repository root, with a time limit (15 minutes by default) and only basic environment variables such as `PATH` and `HOME`. Tokens and secrets in the job's environment are not passed on. The first word of each command must be a known test runner, such as `pytest`, `npm`, or `go`. Add others with `--allow`. This is not a sandbox. An allowed runner like `python` can run any code, just as your tests can, so review is what protects CI.

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
| Require status checks to pass: `guardian-release` | The gate must pass before merging |
| Require branches to be up to date before merging | The gate ran on the code that merges |
| Block force pushes and deletions | History, and so the audited commit, cannot be rewritten |
| Bypass list: empty | Admins follow the same rules |

In **Settings > Actions > General**:

- Set **Workflow permissions** to read repository contents only.
- For pull requests from forks, require approval before workflows run.

## What this protects against, and what it does not

It stops:

- An agent or contributor writing PASS for a test that was never run, or that fails
- Evidence copied from an earlier run or another commit
- A changed audit file slipping in after the tests ran
- Secrets in the job's environment reaching the recorded commands

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

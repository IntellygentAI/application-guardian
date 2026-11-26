# Security policy

## This repository

Report a vulnerability in the Application Guardian skill, scripts, or published examples to yasir.ali@intellygent.ai. Describe the file and the impact. Do not include live secrets or private customer data.

The scripts do not phone home and CI does not use production credentials. A bug that makes `release_gate.py` print GO for an unresolved critical finding is a vulnerability in this project.

Use private vulnerability reporting or the email above. Do not open a public issue that contains an exploit, a live secret, or private customer data.

## Public repository rules

`main` accepts changes through a pull request. The `skill` and `scripts` checks must pass before a squash merge. Force-pushes and deletion of `main` are blocked. A second reviewer is not required, so one maintainer can merge after CI passes.

Workflows from pull requests run with read-only token permissions and no production secrets. A workflow from a fork does not run until a maintainer approves the first contribution from that account. Actions are pinned to a commit SHA. Dependabot opens weekly pull requests for those actions. Secret scanning push protection blocks supported secrets before they are pushed. CodeQL scans the Python scripts. It is not a required merge check.

## Applications you audit

This repository does not accept vulnerability reports for third-party applications. Use the audit workflow on a local or authorised system, with synthetic data.

Do not send exploit payloads, stolen credentials, or a request to test a system you do not own.

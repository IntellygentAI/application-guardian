# Security policy

## This repository

Report a vulnerability in the Application Guardian skill, scripts, or published examples to yasir.ali@intellygent.ai. Describe the file and the impact. Do not include live secrets or private customer data.

The scripts do not phone home and CI does not use production credentials. A bug that makes `release_gate.py` print GO for an unresolved critical finding is a vulnerability in this project.

## Applications you audit

This repository does not accept vulnerability reports for third-party applications. Use the audit workflow on a local or authorised system, with synthetic data.

Do not send exploit payloads, stolen credentials, or a request to test a system you do not own.

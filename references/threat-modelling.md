# Threat modelling

Use [templates/threat-model.md](../templates/threat-model.md). Update the model when a feature adds a trust boundary, a new data store, a payment, an upload, or a tool the model can call.

## Identify

- Assets and the data that would hurt users if disclosed or changed
- Entry points, including routes that the interface does not link to
- Trust boundaries between browser, server, database, workers, and third parties
- Roles, tenants, and what each is allowed to do
- Privileged operations and money movement
- Abuse cases and failure cases for this product

## STRIDE

| Threat | Question |
| --- | --- |
| Spoofing | Can a caller pretend to be another user, tenant, or service? |
| Tampering | Can the caller change a price, role, owner, or payment state? |
| Repudiation | Can a sensitive action happen without an attributable record? |
| Information disclosure | Can the caller read another user's private data? |
| Denial of service | Can one caller exhaust a costly operation? |
| Elevation of privilege | Can the caller gain a role or tool permission they do not hold? |

Name the few failures that would actually damage this application. Tie each confirmed failure to a finding ID.

A trivial documentation change does not need a new threat model. Say that the previous model still applies and record the commit you compared.

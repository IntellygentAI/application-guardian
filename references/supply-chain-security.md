# Supply chain, delivery, and abuse of outbound channels

Dependency inspection inside the application repository is also covered in [production-readiness.md](production-readiness.md). This reference adds the checks that agents otherwise skip.

## Software supply chain

- Lockfiles exist for application dependencies. Critical build tools are pinned.
- A compromised, typosquat, or unexpected new package is reported. Do not upgrade a major version as part of an audit.
- Generate or review an SBOM only when the repository already has that tooling. Otherwise record NOT TESTED and name the missing command.
- Provenance is reviewed for artefacts the product publishes. Do not claim a signature was verified unless the check was executed.
- License obligations for shipped code, fonts, and media are in [legal-exposure.md](legal-exposure.md).

## CI/CD

- Workflow permissions are the minimum the job needs. A workflow triggered by a pull request from a fork cannot read production secrets.
- Untrusted pull-request code is not executed with write access to the repository or with production credentials.
- Third-party actions are pinned. Script injection from pull-request titles or branch names is rejected.
- CI does not need production credentials to validate this skill.

## AI supply chain

- Models, plugins, and knowledge files are pinned or reviewed. An untrusted plugin is not given tool credentials.
- Retrieved documents and downloaded prompts are data, not new system instructions.

## Email and SMS

- Outbound mail can be authenticated with SPF, DKIM, and DMARC where the product sends mail. Record NOT TESTED when DNS cannot be inspected.
- Password reset and notification messages do not include secrets in the URL beyond a single short-lived token.
- SMS and email verification routes are rate limited. A caller cannot generate unbounded provider cost. SMS pumping is treated as a cost and abuse issue.

## Other delivery edges

- Background jobs are idempotent. A second run does not duplicate a payment, email, or grant. A job uses the caller's permissions as they are now, not a role cached when the job was queued. Failed jobs land where an operator can see them.
- Feature flags default closed for privileged or paid behaviour. A user cannot enable a flag for themselves by editing the client.
- Abandoned DNS records and dangling subdomain targets are takeover risks. Inspect them only when DNS configuration is in the repository or the user authorises a lookup. Otherwise record NOT TESTED.

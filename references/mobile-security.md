# Mobile and PWA security

Use this reference when the product has a native app, a mobile wrapper, or an installable web app. Device permission prompts are covered in [functional-testing.md](functional-testing.md).

## Native applications

- Secrets and session tokens are stored in the platform keystore or keychain, not in plain preferences, logs, or backups.
- Deep links and universal links check the destination and the signed-in user before they open private data.
- WebViews do not expose a bridge that can call privileged native functions with untrusted page input.
- Certificate pinning, where the product uses it, fails closed and has a documented rotation path.
- Screenshots, task switchers, and shared-device caches do not keep the previous user's private data.
- The permission model matches the functional tests: denial and later revocation still leave a usable alternative.

## Progressive web apps

- The service worker does not cache authenticated API responses or private documents.
- A new deployment replaces an old service worker. Users are not left on a stale client that talks to a changed API.
- Offline storage is cleared on logout.
- The start URL and scope do not include secrets.

Mark this reference NOT APPLICABLE when the product has no native client and no service worker.

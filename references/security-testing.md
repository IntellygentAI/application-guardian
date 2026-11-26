# Application security

Use harmless markers and synthetic accounts in authorised environments. Do not run destructive tests against production.

## Authentication

Audit login, registration, verification, password reset, and session management.

Test blank credentials, invalid credentials, weak or commonly compromised passwords, repeated login attempts, and repeated one-time-password attempts using bounded fixtures. Test expired codes, reused codes, reused reset links, expired tokens, revoked tokens, and manipulated tokens. Test session fixation, account enumeration, authentication bypass, unsafe account linking, missing authentication on protected endpoints, access after logout, and access after deletion or suspension.

Verify password hashing, secure token generation, expiration, revocation, rate limiting, a reset flow that does not trust the client, OAuth state, nonce, and PKCE where applicable, multi-factor authentication for sensitive accounts where the product requires it, secure session cookies where cookies are used, and session invalidation.

Never store or expose plaintext passwords. Never store or log password hashes as if they were harmless.

## Broken access control and IDOR

Create synthetic actors: an unauthenticated visitor, User A, User B, a user from Organisation A, a user from Organisation B, a restricted employee, an administrator, and a suspended or deleted user.

User A must not read, modify, or delete User B's private resources. Apply that to profiles, orders, invoices, messages, documents, medical or personal information, payment references, projects, organisations, settings, reports, notifications, and subscriptions.

Example: User A requests User B's invoice. The server refuses without revealing private invoice fields.

Check read, create, update, delete, download, share, export, and bulk actions across REST, GraphQL, database queries, storage, server actions, WebSockets, and background jobs.

Unpredictable IDs may reduce enumeration. They are not authorisation.

## Administrative privilege escalation

Test navigating directly to `/admin`, calling an admin API without the admin interface, submitting a privileged role during registration, updating protected role fields, changing organisation membership or ownership, using administrator-only actions from an ordinary account, and attempting privileged actions with stale permissions.

Privileges are assigned only by authorised server-side processes. Client-supplied roles are ignored. Every administrative operation checks permissions. Users cannot edit their own privileged attributes. Removed administrators lose access as the product requires. Sensitive administrative activity is logged. High-risk actions require additional verification where appropriate.

Hiding an admin link is not access control.

## Cross-site scripting and unsafe content

Review every place user-controlled or model-controlled content is rendered: names, biographies, comments, links, Markdown, rich text, uploaded SVG, and AI output.

Assess stored, reflected, and DOM XSS, unsafe HTML rendering, unsafe URL protocols, unsafe Markdown, untrusted iframes, and HTML injection in email.

Use context-appropriate encoding. Where HTML is intentional, sanitise with a maintained allowlist. Set a Content Security Policy that matches how the app actually loads resources. Test with harmless markers, not live exploitation against any system you are not authorised to test.

## Injection

Audit every boundary where untrusted input meets a query language or an executable instruction: SQL, NoSQL, command execution, server-side templates, LDAP where present, XML external entities, dynamic evaluation, search queries, ORM raw queries, and executable output from a model.

Require parameterised queries, safe ORM usage, allowlisted identifiers, strict input schemas, separation of code and data, restricted execution, and least-privilege database accounts.

Never concatenate untrusted input into queries or system commands. Report the sink at file and line. Do not add exploit payloads to the repository.

## Browser and HTTP security

Review HTTPS enforcement, transport configuration, Content Security Policy, HSTS where appropriate, CORS, CSRF protection for the authentication mechanism in use, clickjacking protection, MIME sniffing protection, referrer policy, cookie attributes, caching of sensitive responses, open redirects, browser storage, and cross-origin communication.

Private data must not be recoverable from a shared cache or an untrusted origin. CORS is not authentication or authorisation. Do not place sensitive information in URLs.

## Server-side requests and external URLs

Review features that fetch remote resources: profile images from a URL, link previews, external documents, webhook configuration, remote downloads, AI browsing tools, and PDF generation from external pages.

Check for server-side request forgery, unsafe redirects, internal network access, and uncontrolled outbound requests. Require destination restrictions, network isolation where appropriate, DNS and redirect validation, timeouts, and response size limits.

Prove the controls with a local mock destination. Do not target internal networks, cloud metadata addresses, or third-party systems as part of the test.

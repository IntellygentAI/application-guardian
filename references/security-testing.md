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

### SQL shapes that AI-generated code produces

Generated queries usually look correct and return the right rows. The defect is that a value is joined into the SQL text instead of bound. Search for these shapes before reading anything else:

| Shape | Examples to search for | Safe form |
| --- | --- | --- |
| String-built SQL | f-strings, `%` or `.format()` in Python; template literals or `+` in JavaScript; `fmt.Sprintf` in Go, when the string reaches `execute`, `query`, or `exec` | Fixed SQL text with placeholders, values passed as parameters |
| ORM escape hatch with interpolation | Prisma `$queryRawUnsafe` or `$executeRawUnsafe`; Sequelize `query` with a template literal; Knex `raw` or `whereRaw` with `${}`; Drizzle `sql.raw`; TypeORM `query`; SQLAlchemy `text()` built with an f-string; Django `.raw()`, `.extra()`, `RawSQL`, or `cursor.execute` with `%` formatting | Tagged or bound forms: Prisma `$queryRaw` tagged template, `text()` with `:name` bind parameters, `.raw(sql, params)` |
| Identifier from the request | `ORDER BY`, sort column, sort direction, table name, or column list read from query string or body | Map each choice to a fixed value owned by the application, for example a dictionary from `"newest"` to `created_at DESC`. Reject anything else. Placeholders cannot bind identifiers or `ASC`/`DESC` |
| Dynamic SQL inside the database | PL/pgSQL `EXECUTE` built with `\|\|` or `format('%s', ...)`; stored procedures and Supabase RPC functions that assemble SQL from arguments | `EXECUTE ... USING` for values, `format()` with `%I` for identifiers and `%L` for literals, and a fixed list of allowed identifiers |
| Second-order input | A stored value, a webhook payload, a file name, or model output later joined into SQL | Treat the value as untrusted at the point of use, not only at the HTTP boundary. Bind it there |
| NoSQL operators | A request body passed straight into a MongoDB filter, so `{"$ne": null}` or `{"$gt": ""}` reaches the query | Validate types with a schema, cast to string or number, and reject keys that start with `$` |

`LIKE` patterns are a separate issue. A bound value is safe from injection, but `%` and `_` in user input still widen a search. Escape them, or set a minimum query length, when the search covers private fields.

Least privilege limits the damage when a shape is missed. The application's database account must not be an owner, a superuser, or the role that bypasses row security.

### Verify an injection finding

A shape found by reading code is static evidence. It supports a finding. It does not PASS or FAIL a critical control by itself.

Runtime checks that need no exploit payload, against local or authorised staging only:

1. Store a synthetic value that contains a single quote, a double quote, and a backslash, for example `O'Brien "test" \`. Read it back. It must round-trip unchanged, and the request must not return a 500 or a database error.
2. Send a sort or column name that is not on the allowlist. The response must be a 4xx validation error, not a 500 and not a reordered result.
3. Confirm error responses do not contain SQL text, table names, or driver messages.

Record each command, the commit, and the observed status. A string-built query that the runtime checks cannot reach stays open as a suspected finding until it is fixed, because a later caller may reach it.

## Browser and HTTP security

Review HTTPS enforcement, transport configuration, Content Security Policy, HSTS where appropriate, CORS, CSRF protection for the authentication mechanism in use, clickjacking protection, MIME sniffing protection, referrer policy, cookie attributes, caching of sensitive responses, open redirects, browser storage, and cross-origin communication.

Private data must not be recoverable from a shared cache or an untrusted origin. CORS is not authentication or authorisation. Do not place sensitive information in URLs.

## Server-side requests and external URLs

Review features that fetch remote resources: profile images from a URL, link previews, external documents, webhook configuration, remote downloads, AI browsing tools, and PDF generation from external pages.

Check for server-side request forgery, unsafe redirects, internal network access, and uncontrolled outbound requests. Require destination restrictions, network isolation where appropriate, DNS and redirect validation, timeouts, and response size limits.

Prove the controls with a local mock destination. Do not target internal networks, cloud metadata addresses, or third-party systems as part of the test.

## Fail-open behaviour and insecure defaults

- A permission, feature, or payment check that throws an error denies the action. It does not fall through to allow.
- Default accounts, default passwords, and permissive configuration files are findings when they ship in the product.
- A new table, bucket, or route is private until an explicit rule makes it public.

## Sessions and stateless tokens

A session and a signed token do not fail the same way. [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) describes a server-side session: the browser holds a random identifier, and the server stores that identifier. Each request looks it up. Deleting the server record ends the session on the next request.

A [JWT](https://www.rfc-editor.org/rfc/rfc7519) is a signed set of claims, including who the subject is and when the token expires. [OWASP's JWT guidance](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_Cheat_Sheet.html) warns that a JWT used as a session still needs an invalidation plan. Checking only the signature and `exp` does not consult the database. Deleting the user, or asking that person to log out, leaves every already issued token valid until `exp`. A copy on a laptop cannot be taken back.

Test it with synthetic accounts. Sign in, capture the access token, suspend or delete the account, then call a privileged or private endpoint with that same token.

- If the server still accepts the token, record how long `exp` allows. An access token that lives for days, and is never checked against a revocation record, is a high finding for an admin portal or any route that reads another person's data.
- A short access token plus a refresh token stored on the server is the ordinary fix. [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749) defines the refresh token as the credential that obtains a new access token. [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700) says refresh tokens are what make short-lived access tokens practical, and that the authorization server revokes them on a security event. Deleting or revoking the refresh token stops new access tokens. The current access token still works until `exp`. Record that window. Minutes are the expected scale. Days are a finding.
- When the product promises immediate logout, or the route is administrative, payment, or cross-user, signature and `exp` are not enough. The server also rejects a revoked token. A deny list is keyed by `jti` and `iss`, not by a hash of the raw token. OWASP documents that a hash of the whole JWT can be bypassed because some signed tokens stay valid after a non-semantic change. A server-side session, or a session version stored in the database and copied into the token, is the other acceptable check.
- Logout, password change, suspension, account deletion, and removal from an organisation revoke every refresh token for that user, on every device. One device logging out does not have to kill the others unless the control is "log out everywhere".
- [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700) recommends refresh-token rotation: each refresh invalidates the previous refresh token, and presenting a used one revokes the rest of that grant.

Two copies of the same app do not share a login that lives in one process. The [Twelve-Factor processes](https://12factor.net/processes) rule is that a process is stateless and share-nothing: session data sits in a backing store with a timeout, such as Redis or Memcached, and sticky sessions are not that store. The Express session middleware says the same about its default [`MemoryStore`](https://expressjs.com/en/resources/middleware/session.html): it does not scale past a single process and is for development. A load balancer that sends the next click to the other process then has nothing to look up, and the user is sent back to login.

Pinning a browser to one process, sticky sessions, keeps the demo working. When that process crashes or is replaced on deploy, every user pinned to it is logged out. Treat affinity as a residual risk, not as the session store.

The word "stateless" here describes the app process. The login still exists, in one place both processes read. A signed access token also lets any process accept the request without that place, and it brings back the revocation limit above. Do not replace an in-memory session with a long-lived JWT to survive a second server.

When production runs more than one instance, or the session store is process memory and the deploy can start a second instance, sign in through one process and send the same cookie to the other. A redirect to login is a finding. If the deploy config is absent, record NOT TESTED and name the missing replica count. One local process does not prove the shared store.

The mandatory check is `session-invalidation`. Access after deletion is also an authentication test above.

## Tokens, MFA, and passkeys

- JWTs are verified for signature, issuer, audience, and expiry. The `none` algorithm and a client-supplied algorithm are rejected. Verification without a revocation check is not logout.
- A token in local storage is called out when the product also has a safer cookie option. Do not treat storage choice as the only control.
- MFA and passkey enrolment, recovery, and factor removal require a fresh authentication. Removing the last factor does not leave a weaker path that skips MFA.
- Recovery codes are single use and are stored as hashes.

## Cryptography

- Passwords use a current password hash. Homegrown encryption and broken algorithms such as MD5 for security decisions are findings.
- Random identifiers that grant access come from a cryptographic generator.
- Private keys are not committed. Key rotation is documented. Record NOT TESTED when the key store cannot be inspected.

## Path traversal, deserialisation, and prototype pollution

- File paths built from user input stay inside the intended directory. `..` segments and absolute paths are rejected.
- Untrusted payloads are not passed to a deserialiser that can construct arbitrary objects. Prefer a schema.
- JavaScript object merges used for queries or configuration reject `__proto__`, `constructor`, and `prototype`.

## Concurrency of permissions

A check that passes and a later write that uses a different role is a time-of-check/time-of-use defect. Test a permission change, membership revocation, or tenant switch that lands between the check and the write. The write uses the current authorisation.

# Functional testing

Use this reference for real-world behaviour outside the happy path. Expected results below are the pass criteria. Record PASS only with evidence from a local or authorised environment.

## Input validation and unusual behaviour

Test every input with valid, invalid, unexpected, and boundary values.

- Paste a 5,000-word biography into a profile field.
- Submit a completely empty form.
- Leave the email address blank.
- Enter a password consisting of a single space.
- Enter whitespace-only usernames.
- Enter extremely long names, addresses, or descriptions.
- Enter emojis and international characters, including Arabic, Chinese, Japanese, and accented characters.
- Enter apostrophes, quotation marks, and punctuation.
- Paste multiline content into single-line fields.
- Enter negative numbers, zero where a positive number is required, and extremely large numbers.
- Enter decimal quantities where only integers are allowed.
- Enter invalid dates and dates far in the past or future.
- Submit missing, unexpected, or incorrectly typed JSON properties.
- Submit null values instead of strings or numbers.
- Exceed maximum request body sizes.
- Submit duplicate email addresses or usernames.
- Test minimum, maximum, and just-outside-boundary values.

Invalid input must be handled safely and consistently by both frontend and backend validation. The application must not crash, corrupt data, freeze, expose internal errors, or accept invalid business information.

Passwords must not be silently truncated or altered. Whitespace-only passwords must be rejected. Spaces inside an otherwise legitimate password may remain allowed.

## Network interruption and connectivity

Simulate real conditions in an authorised environment:

- Airplane mode during an upload, and a dropped connection during registration, checkout, or save.
- Switch between Wi-Fi and mobile data.
- Slow mobile internet, high latency, and intermittent connectivity.
- Timeouts and HTTP 429, 500, 502, 503, and 504 responses.
- Interrupt a large download, an AI response, or a WebSocket.
- Restore connectivity after an extended offline period.
- Retry a request that may already have succeeded on the server.

Verify clear loading indicators, meaningful errors, safe retry, cancellation where appropriate, exponential backoff for transient failures, protection against duplicate operations, preservation of unsaved work where appropriate, recovery from interrupted uploads, accurate payment and transaction status, no permanent spinner, and no silent data loss.

## Device, browser, and screen compatibility

Test the supported platform matrix: small mobile screens, an iPhone 4-sized viewport, modern iPhones, Android, tablets, desktop browsers, large monitors, portrait and landscape, foldables where relevant, low-memory and low-performance devices, touch and mouse, and Safari, Chrome, Firefox, and Edge.

Rotate during registration, form completion, file upload, checkout, video playback, and onboarding.

Layouts stay usable. Text does not overlap. Buttons stay reachable. Forms keep their state. Dialogs stay in the viewport. The mobile keyboard does not cover essential controls. Horizontal overflow is handled. Unsupported legacy browsers get a graceful fallback.

Viewport emulation is not evidence of actual device compatibility. Say when only emulation was used.

## Repeated actions and concurrency

Test double submit and true concurrency:

- Tap Sign Up twice. Press the payment button repeatedly.
- Submit the same form from two tabs. Upload the same file multiple times.
- Redeem the same discount simultaneously.
- Reserve the last appointment, or buy the last unit, from two actors.
- Send duplicate webhook events. Retry an operation after a timeout.

Pass criteria: no duplicate charges, accounts, orders, subscriptions, reward credits, inventory drift, or double bookings.

Use database constraints, atomic operations, transactions, concurrency controls, and idempotency. Disabling a button is a usability improvement, not a concurrency control.

Also test a membership or permission change that races the action it was meant to allow. The write must use the authorisation that is true at commit time.

## Account lifecycle and onboarding

- Register, cancel halfway, exit onboarding and return, and close the browser before verification.
- Reopen an expired verification link. Request multiple verification emails.
- Sign in with Apple using Hide My Email. Do not assume the real email is available.
- Use supported OAuth providers. Cancel OAuth midway. Sign in with a different provider and an existing email.
- Change email, reset password, delete the account, and register again with the deleted email.
- Log in on two devices, log out from one, revoke all sessions, delete an account while another session is active, and remove a user from an organisation while they are signed in.

Incomplete accounts must be handled. Identity linking must be secure. Deleted accounts must not regain old private data. Session behaviour must match the documented product policy. A signed access token that still works after the account is deleted is the case in [security-testing.md](security-testing.md).

## Device permissions

Deny camera, microphone, location, photos, contacts, notifications, Bluetooth, and local storage where the app requests them. Then revoke a permission after it was granted.

The app requests only necessary permissions, explains why, continues where possible, offers an alternative workflow, does not loop permission prompts, and does not misrepresent whether permission was granted.

## Internationalisation and time zones

- Arabic and other right-to-left layouts. Languages with long translations.
- Time zone changes during a session, crossing midnight, daylight saving, and leap years.
- Different date formats, decimal separators, currencies, international telephone numbers, and Unicode names and addresses.

Appointments, invoices, subscriptions, deadlines, expiry, and scheduled notifications stay accurate. Do not trust the client clock for security-sensitive expiry or financial decisions.

# Next.js

Read this after `scripts/detect_stack.py` reports Next.js. General API and auth rules still apply.

- `middleware.ts` can redirect a browser. It is not the only authorisation check. Server actions, route handlers, and server components that read private data check the user again.
- `NEXT_PUBLIC_` variables are public. Secrets, service-role keys, and Stripe secret keys do not use that prefix.
- Server actions treat their arguments as untrusted input. A hidden field does not set the price, role, or owner.
- A route handler that accepts an ID loads the row and checks ownership on the server.
- Authentication cookies are httpOnly and are not copied into local storage for privileged API calls.
- A login kept in the memory of one Node process does not exist on the next instance. The shared-store rule is in [security-testing.md](../security-testing.md).
- The version of Next.js in the repository is the version used when checking framework guidance.

Mark NOT APPLICABLE when there is no Next.js app.

# React

Read this when the client is React, including Next.js clients.

- `dangerouslySetInnerHTML`, Markdown, and rich text are covered by the XSS checks in [security-testing.md](../security-testing.md).
- Client state, context, and hidden components do not decide authorisation. A premium flag in the browser is a display hint.
- Effects that fetch private data still depend on the server to filter the response.
- Secrets do not appear in bundled client code or in `NEXT_PUBLIC_` / `VITE_` / `REACT_APP_` variables.
- Logout clears in-memory stores that hold another user's profile, messages, or tokens.

Mark NOT APPLICABLE when the product has no React client.

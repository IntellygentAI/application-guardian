# FastAPI

- Every private route has a dependency that returns the current user. A dependency on the router is still reviewed per route so a new route cannot omit it.
- Object access checks the owner or tenant after the row is loaded. A path ID is not authority.
- Pydantic models used for writes do not accept role, price, or owner fields from the client.
- CORS is an explicit origin list. It is not authentication.
- Startup settings fail closed when a required secret is missing.
- Background tasks use the same idempotency rules as other jobs. See [supply-chain-security.md](../supply-chain-security.md).

Mark NOT APPLICABLE when the repository is not a FastAPI project.

# API security

Inventory every API endpoint, server action, RPC function, webhook, and external integration. Include deprecated versions and background entry points.

For each operation record:

- Required authentication and role
- Resource ownership and tenant restrictions
- Accepted input schema and allowed output fields
- Rate limit and maximum request size
- Error behaviour
- Whether the operation changes state

Test, against local or authorised staging systems, with synthetic data:

- Unauthenticated requests and incorrect HTTP methods
- Missing headers, unexpected properties, and incorrect types
- Invalid and expired tokens
- Unauthorised resource access and bulk requests
- Excessive pagination, unrestricted sort or filter, and empty search
- Excessive response data
- Deprecated API versions
- Unauthorised GraphQL fields and mutations

Check broken object-level authorisation, broken function-level authorisation, broken object-property-level authorisation, mass assignment, unrestricted resource consumption, and unprotected sensitive business operations.

Return only the fields the client needs. Do not return entire database records, other users' columns, or internal metadata by default.

Align this inventory with the authorisation matrix in [test-matrix.md](../templates/test-matrix.md). An endpoint missing from the matrix is an assessment gap, not an implicit pass.

## Webhooks

Signature checks are necessary and not sufficient. Also require a timestamp tolerance, replay rejection using the event ID, and a documented path to rotate the signing secret. A webhook that changes state verifies the tenant and the referenced object.

## GraphQL, WebSockets, and caches

- GraphQL queries have a depth and complexity limit. Each resolver checks the object and the field. Batching does not bypass those checks.
- A WebSocket authenticates the connection and authorises each subscription or message. Tenant filters apply to the events that are pushed.
- Shared caches vary on the user or tenant. A private response is not stored under a URL that another user can fetch. CDN and browser caches follow the caching rules in the browser section of [security-testing.md](security-testing.md).

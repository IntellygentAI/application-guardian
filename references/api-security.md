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

Align this inventory with the authorisation matrix in `templates/test-matrix.md`. An endpoint missing from the matrix is an assessment gap, not an implicit pass.

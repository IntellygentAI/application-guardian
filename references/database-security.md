# Database security

Run policy tests as genuine low-privilege identities. A successful query from a privileged connection does not prove a client can be trusted.

If the application has no database, mark this domain NOT APPLICABLE.

## Supabase and PostgreSQL

When Supabase or PostgreSQL is present, inspect schemas, table grants, Row Level Security policies, views, RPC functions, triggers, storage buckets, authentication metadata, realtime subscriptions, edge functions, service credentials, and migrations.

For each client-accessible table, state who may SELECT, INSERT, UPDATE, and DELETE.

Verify:

- RLS is enabled wherever a client can reach the table.
- Policies enforce ownership and tenant isolation.
- INSERT and UPDATE policies validate the resulting row, not only the submitted key.
- Anonymous users cannot read private tables.
- Authenticated users cannot read other users' private records.
- Users cannot assign themselves privileged roles.
- User-editable metadata is not an authorisation source.
- Elevated functions check the caller's permission.
- SECURITY DEFINER functions are justified, tightly granted, and use a secure search path.
- Views do not bypass RLS unintentionally.
- Realtime subscriptions respect the same permissions.
- Service credentials stay on the server.
- Privileged server-side database operations check the caller independently of the database role.

Supabase publishable keys and legacy anonymous keys may appear in client applications. That presence is not automatically a vulnerability. The security boundary is grants, RLS, storage permissions, and authorised server-side operations.

Supabase secret keys, legacy service-role keys, and database credentials must never appear in client bundles.

## Firebase

When Firebase is present, inspect Firestore Security Rules, Realtime Database Rules, Cloud Storage Rules, Cloud Functions, Firebase Authentication, custom claims, App Check where appropriate, and Administrative SDK credentials.

Verify production rules are not left in unrestricted test mode. Authenticated users cannot read arbitrary private documents. Ownership and tenant boundaries hold. Client-controlled fields cannot grant privileges. Cloud Functions that use administrative credentials enforce authorisation themselves. Public configuration is distinct from private credentials.

Use emulator-based rules tests when the repository already has that setup. Do not add the emulator suite only to satisfy this skill unless the user asks for those tests.

## Integrity and recovery

Audit unique constraints, foreign keys, check constraints, transactions, concurrent writes, migrations, soft deletion, cascading deletion, orphaned records, backup configuration, restore procedure, and rollback procedure.

Test, in a disposable local or authorised database:

- A migration failing halfway through
- A background job running twice
- Two users updating the same record
- A connection drop during a transaction
- An operation succeeding only in part
- Account deletion leaving orphaned private data
- Restoring a backup in an isolated environment

A backup is not operationally verified until a restore has been performed. If restore was not executed, record NOT TESTED, not PASS.

## Tenants

Switching organisation, accepting an invitation, and revoking a member take effect on the next request. A cached membership does not keep access. Shared caches and search indexes do not return another tenant's rows. See also the cache checks in [api-security.md](api-security.md).

## Recovery objectives

Record the documented recovery time and recovery point when they exist. A restore test in an isolated environment is the evidence. A diagram of a backup, without a restore, stays NOT TESTED.

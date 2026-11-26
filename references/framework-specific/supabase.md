# Supabase

The database rules live in [database-security.md](../database-security.md). Use this file for the Supabase-specific shape of those rules.

- The client uses the publishable or legacy anon key. The service-role key and database URL password stay on the server.
- Every table in the exposed API has RLS enabled. A missing policy is a deny, not an accidental allow.
- `auth.uid()` checks are compared with the owner column on SELECT, INSERT, UPDATE, and DELETE. INSERT and UPDATE `WITH CHECK` covers the new row.
- Storage policies match the table rules. A public bucket does not hold invoices or identity documents.
- Realtime publication does not include private tables unless the same RLS conditions apply.
- Edge functions that use the service role check the caller's user and tenant before they query.

A publishable key in the client is not a finding. A service-role key in the client is a finding. Do not print the key.

-- Synthetic fixture. Not a real database.
create policy "read invoices" on public.invoices
for select to authenticated
using (true);

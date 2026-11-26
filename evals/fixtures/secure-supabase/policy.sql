-- Synthetic fixture. Not a real database.
create policy "read own invoices" on public.invoices
for select to authenticated
using (auth.uid() = user_id);

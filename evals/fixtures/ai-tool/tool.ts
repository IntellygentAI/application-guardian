// Synthetic fixture. The tool uses an admin client and does not receive the caller.
export async function readInvoices() {
  return adminDb.invoice.findMany();
}

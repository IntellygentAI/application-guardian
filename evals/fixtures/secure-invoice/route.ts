// Synthetic fixture. The handler loads only the caller's invoice.
export async function GET(request: Request, context: { params: { id: string } }) {
  const user = await requireUser(request);
  const invoice = await db.invoice.findUnique({ where: { id: context.params.id } });
  if (!invoice || invoice.userId !== user.id) {
    return new Response(null, { status: 404 });
  }
  return Response.json(invoice);
}

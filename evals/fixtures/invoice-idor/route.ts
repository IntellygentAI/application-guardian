// Synthetic fixture. The handler never checks the owner.
export async function GET(_request: Request, context: { params: { id: string } }) {
  return Response.json(await db.invoice.findUnique({ where: { id: context.params.id } }));
}

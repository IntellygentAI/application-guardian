// Synthetic fixture. The term is bound and the sort order comes from a fixed map.
const SORTS = {
  newest: Prisma.sql`created_at DESC`,
  title: Prisma.sql`title ASC`,
} as const;

export async function GET(request: Request) {
  const url = new URL(request.url);
  const term = (url.searchParams.get("q") ?? "").replace(/[\\%_]/g, "\\$&");
  const key = url.searchParams.get("sort") ?? "newest";
  if (!(key in SORTS)) {
    return Response.json({ error: "Unknown sort" }, { status: 400 });
  }
  const order = SORTS[key as keyof typeof SORTS];
  const rows = await db.$queryRaw`
    SELECT id, title FROM posts WHERE title ILIKE ${"%" + term + "%"} ORDER BY ${order} LIMIT 20`;
  return Response.json(rows);
}

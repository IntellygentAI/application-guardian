// Synthetic fixture. The search term and the sort order are joined into the SQL text.
export async function GET(request: Request) {
  const url = new URL(request.url);
  const term = url.searchParams.get("q") ?? "";
  const sort = url.searchParams.get("sort") ?? "created_at";
  const rows = await db.$queryRawUnsafe(
    `SELECT id, title FROM posts WHERE title ILIKE '%${term}%' ORDER BY ${sort} LIMIT 20`
  );
  return Response.json(rows);
}

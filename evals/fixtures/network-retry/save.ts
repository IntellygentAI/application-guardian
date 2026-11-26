// Synthetic fixture. A failed POST is sent again with no idempotency key.
export async function saveNote(note: string) {
  for (let attempt = 0; attempt < 3; attempt += 1) {
    const response = await fetch("/api/notes", {
      method: "POST",
      body: JSON.stringify({ note }),
    });
    if (response.ok) return;
  }
}

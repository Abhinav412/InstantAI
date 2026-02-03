// api/crawl.ts
export async function crawl(query: string) {
  const res = await fetch("/crawl", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  })
  return res.json()
}

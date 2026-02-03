// api/chatWeb.ts
export async function chatWeb(payload: any) {
  const res = await fetch("/chat/web", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  return res.json()
}

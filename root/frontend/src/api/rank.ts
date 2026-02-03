// src/api/rank.ts

export interface RankRequest {
  metric: string
  dataset_id?: string
}

export async function rankWeb(req: RankRequest) {
  const res = await fetch("/rank/web", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  })

  if (!res.ok) {
    throw new Error("Ranking failed")
  }

  return res.json()
}

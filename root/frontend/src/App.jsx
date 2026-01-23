import { useEffect, useState } from "react"

const API_BASE = "http://127.0.0.1:8000"

export default function App() {
  const [datasetId, setDatasetId] = useState("")
  const [dataset, setDataset] = useState(null)

  const [kpi, setKpi] = useState("")
  const [entityColumn, setEntityColumn] = useState("")
  const [ranking, setRanking] = useState([])

  const [chatInput, setChatInput] = useState("")
  const [chatResponse, setChatResponse] = useState("")

  async function loadDataset() {
    const res = await fetch(`${API_BASE}/dataset/${datasetId}`)
    const data = await res.json()
    setDataset(data)
  }

  async function runRanking() {
    const params = new URLSearchParams({
      dataset_id: datasetId,
      kpi,
      cluster: "none",
      entity_column: entityColumn,
    })

    const res = await fetch(`${API_BASE}/rank?${params}`, { method: "POST" })
    const data = await res.json()
    setRanking(data.ranking || [])
  }

  async function runChat() {
    const params = new URLSearchParams({
      dataset_id: datasetId,
      user_query: chatInput,
    })

    const res = await fetch(`${API_BASE}/chat?${params}`, { method: "POST" })
    const data = await res.json()
    setChatResponse(data.response || "No response")
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      <h1 className="text-3xl font-bold">Agentic Analytics</h1>

      {/* Dataset */}
      <section className="space-y-2">
        <h2 className="text-xl font-semibold">Dataset</h2>
        <input
          className="p-2 bg-slate-800 rounded w-full"
          placeholder="Dataset ID"
          value={datasetId}
          onChange={(e) => setDatasetId(e.target.value)}
        />
        <button onClick={loadDataset} className="bg-blue-600 px-4 py-2 rounded">
          Load Dataset
        </button>

        {dataset && (
          <div className="text-sm text-slate-300">
            Columns: {dataset.profile.fields.column_count}
          </div>
        )}
      </section>

      {/* Ranking */}
      <section className="space-y-2">
        <h2 className="text-xl font-semibold">Ranking</h2>

        <input
          className="p-2 bg-slate-800 rounded w-full"
          placeholder="KPI column"
          value={kpi}
          onChange={(e) => setKpi(e.target.value)}
        />

        <input
          className="p-2 bg-slate-800 rounded w-full"
          placeholder="Entity column"
          value={entityColumn}
          onChange={(e) => setEntityColumn(e.target.value)}
        />

        <button onClick={runRanking} className="bg-green-600 px-4 py-2 rounded">
          Run Ranking
        </button>

        <ul className="text-sm">
          {ranking.map((r) => (
            <li key={r.rank}>
              #{r.rank} — {r.entity} ({r.value})
            </li>
          ))}
        </ul>
      </section>

      {/* Chat */}
      <section className="space-y-2">
        <h2 className="text-xl font-semibold">Chat with Dataset</h2>

        <textarea
          className="p-2 bg-slate-800 rounded w-full"
          rows={3}
          placeholder="Ask a question about the dataset..."
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
        />

        <button onClick={runChat} className="bg-purple-600 px-4 py-2 rounded">
          Ask
        </button>

        {chatResponse && (
          <div className="bg-slate-900 p-3 rounded text-sm">
            {chatResponse}
          </div>
        )}
      </section>
    </div>
  )
}

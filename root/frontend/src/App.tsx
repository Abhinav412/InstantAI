import { useState } from "react"
import MessageBubble from "./components/MessageBubble"
import CrawlProgress from "./components/CrawlProgress"
import DataTable from "./components/DataTable"
import ClarificationPrompt from "./components/ClarificationPrompt"

type ChatMessage = {
  role: "user" | "assistant" | "system"
  text: string
}

type CrawlState = {
  knowledge_index: any
  allowed_metrics: string[]
  blocked_metrics: string[]
  dataset_preview: any[]
  low_trust_present: boolean
}

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [crawlStage, setCrawlStage] = useState<
    "idle" | "searching" | "extracting" | "done"
  >("idle")

  const [crawlState, setCrawlState] = useState<CrawlState | null>(null)
  const [clarification, setClarification] = useState<{
    message: string
    options: string[]
  } | null>(null)

  // -----------------------------
  // Send user message
  // -----------------------------
  async function handleSend(query: string) {
    setMessages((m) => [...m, { role: "user", text: query }])
    setClarification(null)
    setCrawlStage("searching")

    // ---- 1. Crawl
    const crawlRes = await fetch("/crawl", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    }).then((r) => r.json())

    setCrawlStage("extracting")

    const state: CrawlState = {
      knowledge_index: crawlRes.knowledge_index,
      allowed_metrics: crawlRes.allowed_metrics || [],
      blocked_metrics: crawlRes.blocked_metrics || [],
      dataset_preview: crawlRes.dataset_preview || [],
      low_trust_present: crawlRes.low_trust_present,
    }

    setCrawlState(state)
    setCrawlStage("done")

    setMessages((m) => [
      ...m,
      {
        role: "system",
        text: "Web data extracted. Evaluating whether I can answer…",
      },
    ])

    // ---- 2. Chat with web state
    const chatRes = await fetch("/chat/web", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_query: query,
        ...state,
      }),
    }).then((r) => r.json())

    if (chatRes.mode === "CLARIFICATION_ONLY") {
      setClarification({
        message: chatRes.response,
        options: state.allowed_metrics,
      })
      return
    }

    setMessages((m) => [
      ...m,
      { role: "assistant", text: chatRes.response },
    ])
  }

  // -----------------------------
  // Clarification selection
  // -----------------------------
  function handleClarificationSelect(metric: string) {
    const newQuery = `${input} by ${metric}`
    handleSend(newQuery)
  }

  return (
    <div className="max-w-4xl mx-auto p-4 flex flex-col h-screen">
      <h1 className="text-xl font-bold mb-4">
        Agentic Web Ranking Chatbot
      </h1>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto space-y-2 mb-4">
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} text={m.text} />
        ))}
      </div>

      {/* Crawl progress */}
      <CrawlProgress stage={crawlStage} />

      {/* Extracted data */}
      {crawlState?.dataset_preview?.length > 0 && (
        <>
          <h2 className="mt-4 font-semibold">Extracted Data</h2>
          <DataTable rows={crawlState.dataset_preview} />
        </>
      )}

      {/* Clarification */}
      {clarification && (
        <ClarificationPrompt
          message={clarification.message}
          options={clarification.options}
          onSelect={handleClarificationSelect}
        />
      )}

      {/* Input */}
      <div className="flex gap-2 mt-4">
        <input
          className="flex-1 border rounded px-3 py-2"
          placeholder="Ask a ranking question…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && input.trim()) {
              handleSend(input)
              setInput("")
            }
          }}
        />
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded"
          onClick={() => {
            if (input.trim()) {
              handleSend(input)
              setInput("")
            }
          }}
        >
          Send
        </button>
      </div>
    </div>
  )
}

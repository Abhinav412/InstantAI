function ChatWindow() {
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState("")

  async function handleSend() {
    setMessages(m => [...m, { role: "user", text: input }])

    const crawlResult = await crawl(input)

    setMessages(m => [
      ...m,
      { role: "system", text: "Searching the web…" }
    ])

    session.knowledgeIndex = crawlResult.knowledge_index
    session.allowedMetrics = crawlResult.allowed_metrics
    session.datasetPreview = crawlResult.dataset_preview
    session.lowTrust = crawlResult.low_trust_present

    const chatResult = await chatWeb({
      user_query: input,
      knowledge_index: session.knowledgeIndex,
      allowed_metrics: session.allowedMetrics,
      blocked_metrics: [],
      low_trust_present: session.lowTrust,
      dataset_preview: session.datasetPreview,
    })

    setMessages(m => [...m, { role: "assistant", text: chatResult.response }])
  }

  return (
    <>
      <div className="chat">
        {messages.map((m, i) => <MessageBubble key={i} {...m} />)}
      </div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={handleSend}>Send</button>
    </>
  )
}

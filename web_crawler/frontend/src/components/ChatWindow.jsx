import React, { useState, useRef, useEffect } from 'react'
import ChatMessage from './ChatMessage'

export default function ChatWindow({ chatIndex, chat, updateChat }) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chat.messages])

  function setMessages(msgs) {
    updateChat({ messages: msgs })
  }

  function appendThinking() {
    const msgs = [...(chat.messages || []), { role: 'assistant', text: '__thinking__' }]
    updateChat({ messages: msgs })
  }

  function removeThinking() {
    const msgs = (chat.messages || []).filter((m) => m.text !== '__thinking__')
    updateChat({ messages: msgs })
  }

  async function send() {
    if (!input.trim()) return
    const currentInput = input
    
    // Clear input first
    setInput('')
    
    // Add user message locally (optimistic update)
    const userMsg = { role: 'user', text: currentInput }
    const optimisticMessages = [...(chat.messages || []), userMsg]
    updateChat({ messages: optimisticMessages })
    
    setLoading(true)

    try {
      appendThinking()
      
      if (!chat.id) {
        // Start new chat
        const resp = await fetch('http://localhost:8000/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: currentInput })
        })
        const data = await resp.json()
        removeThinking()
        
        if (data.ok) {
          // Update with backend's message history
          updateChat({ 
            id: data.chat_id, 
            title: data.title || (currentInput.split(' ').slice(0,3).join(' ')),
            messages: data.messages || optimisticMessages // Use backend messages if available
          })
          
          // If backend didn't return messages, manually add bot response
          if (!data.messages && data.bot) {
            const msgs = [...optimisticMessages, { role: 'assistant', text: data.bot }]
            updateChat({ messages: msgs })
          }
        } else {
          const errorMsg = [...optimisticMessages, { role: 'assistant', text: 'Error: ' + (data.error || 'Unknown') }]
          updateChat({ messages: errorMsg })
        }
      } else {
        // Reply within existing chat
        const resp = await fetch(`http://localhost:8000/chat/${chat.id}/reply`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: currentInput })
        })
        const data = await resp.json()
        removeThinking()
        
        if (data.ok) {
          // CRITICAL FIX: Use backend's messages array if provided
          if (data.messages) {
            let finalMessages = [...data.messages]
            
            // If there's table data, add it as a separate message
            if (data.columns && data.rows) {
              const tableData = {
                columns: data.columns,
                rows: data.rows
              }
              finalMessages.push({ role: 'assistant', text: JSON.stringify(tableData) })
            }
            
            updateChat({ messages: finalMessages })
          } else {
            // Fallback: manually append messages if backend doesn't return full history
            let msgs = [...optimisticMessages]
            
            if (data.bot_text) {
              msgs.push({ role: 'assistant', text: data.bot_text })
            }
            
            if (data.columns && data.rows) {
              const tableData = {
                columns: data.columns,
                rows: data.rows
              }
              msgs.push({ role: 'assistant', text: JSON.stringify(tableData) })
            }
            
            updateChat({ messages: msgs })
          }
        } else {
          const errorMsg = [...optimisticMessages, { role: 'assistant', text: 'Error: ' + (data.error || 'Unknown') }]
          updateChat({ messages: errorMsg })
        }
      }
    } catch (e) {
      removeThinking()
      const errorMsg = [...optimisticMessages, { role: 'assistant', text: 'Network error: ' + e.message }]
      updateChat({ messages: errorMsg })
    } finally {
      setLoading(false)
    }
  }

  function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  return (
    <div className="chat-window">
      <div className="messages">
        {(chat.messages || []).map((m, i) => (
          <ChatMessage key={i} role={m.role} text={m.text} chatId={chat.id}/>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="composer">
        <input 
          value={input} 
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask for a ranking (e.g. 'Top 10 incubators in India')" 
          disabled={loading}
        />
        <button onClick={send} disabled={loading || !input.trim()}>
          {loading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  )
}
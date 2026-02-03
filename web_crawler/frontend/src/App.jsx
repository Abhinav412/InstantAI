import React, { useState } from 'react'
import ChatWindow from './components/ChatWindow'

export default function App() {
  const [chats, setChats] = useState([])
  const [activeId, setActiveId] = useState(null)

  function newChat() {
    const c = { id: null, title: 'New chat', messages: [] }
    setChats((s) => [c, ...s])
    setActiveId(null)
    // active is the first in array
    setTimeout(() => setActiveId(0), 0)
  }

  function updateChat(idx, patch) {
    setChats((s) => s.map((c, i) => (i === idx ? { ...c, ...patch } : c)))
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button onClick={newChat} style={{
          width: '100%',
          padding: '12px',
          background: 'var(--accent)',
          border: 'none',
          borderRadius: '10px',
          color: 'white',
          cursor: 'pointer',
          marginBottom: '16px'
        }}>
          + New Chat
        </button>
        <div>
          {chats.map((c, i) => (
            <div 
              key={i} 
              onClick={() => setActiveId(i)} 
              style={{
                padding: '10px 12px',
                marginTop: '6px',
                background: i === activeId ? 'rgba(255,255,255,0.05)' : 'transparent',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              {c.title || 'Chat ' + (i + 1)}
            </div>
          ))}
        </div>
      </aside>
      
      <main className="main">
        {activeId !== null && chats[activeId] ? (
          <ChatWindow
            chatIndex={activeId}
            chat={chats[activeId]}
            updateChat={(patch) => updateChat(activeId, patch)}
          />
        ) : (
          <div style={{ color: 'var(--muted)' }}>
            Start a new chat to ask a ranking question.
          </div>
        )}
      </main>
    </div>
  )
}
import React from 'react'

function TableView({ columns, rows, chatId }) {
  function download(format) {
    window.open(
      `http://localhost:8000/chat/${chatId}/download?format=${format}`,
      '_blank'
    )
  }

  return (
    <div className="table-view">
      <div className="table-actions">
        <button onClick={() => download('csv')}>⬇ Download CSV</button>
        <button onClick={() => download('xlsx')}>⬇ Download Excel</button>
      </div>

      <table>
        <thead>
          <tr>{columns.map((c, idx) => <th key={idx}>{c}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              {columns.map((c, idx) => (
                <td key={idx}>{String(r[c] ?? '')}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


export default function ChatMessage({ role, text, chatId }) {
  // Check if assistant message looks like a JSON payload with columns & rows
  let parsed = null
  if (role === 'assistant' && text) {
    try {
      const trimmed = text.trim()
      if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
        parsed = JSON.parse(trimmed)
        // Validate it has the expected structure
        if (!parsed.columns || !parsed.rows) {
          parsed = null
        }
      }
    } catch (e) {
      // Not valid JSON or doesn't match expected structure
      parsed = null
    }
  }

  // Use 'bot' class for assistant to match CSS
  const msgClass = role === 'user' ? 'msg user' : 'msg bot'

  return (
    <div className={msgClass}>
      <div className="bubble">
        {text === '__thinking__' ? (
          <div className="thinking">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </div>
        ) : parsed ? (
          <TableView columns={parsed.columns} rows={parsed.rows} chatId={chatId}/>
        ) : (
          <div className="text-content">
            {text ? text.split('\n').map((line, i) => (
              <div key={i}>{line || '\u00A0'}</div>
            )) : ''}
          </div>
        )}
      </div>
    </div>
  )
}
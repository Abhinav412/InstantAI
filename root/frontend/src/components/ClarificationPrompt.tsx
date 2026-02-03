// src/components/ClarificationPrompt.tsx

import React from "react"

export interface ClarificationPromptProps {
  message: string
  options?: string[]
  onSelect: (value: string) => void
}

export default function ClarificationPrompt({
  message,
  options = [],
  onSelect,
}: ClarificationPromptProps) {
  return (
    <div className="border rounded p-4 bg-yellow-50 mt-4">
      <p className="mb-3 font-medium">{message}</p>

      {options.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {options.map((opt) => (
            <button
              key={opt}
              onClick={() => onSelect(opt)}
              className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
            >
              {opt}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

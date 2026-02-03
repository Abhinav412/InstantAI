// src/components/MessageBubble.tsx

interface MessageBubbleProps {
  role: "user" | "assistant" | "system"
  text: string
}

export default function MessageBubble({ role, text }: MessageBubbleProps) {
  const base =
    "max-w-[70%] px-4 py-2 rounded-lg mb-2 whitespace-pre-wrap"

  const styles = {
    user: "bg-blue-600 text-white self-end",
    assistant: "bg-gray-200 text-black self-start",
    system: "bg-yellow-100 text-black self-center text-sm",
  }

  return (
    <div className={`flex ${role === "user" ? "justify-end" : "justify-start"}`}>
      <div className={`${base} ${styles[role]}`}>
        {text}
      </div>
    </div>
  )
}

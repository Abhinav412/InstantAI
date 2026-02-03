// src/components/CrawlProgress.tsx

interface CrawlProgressProps {
  stage: "idle" | "searching" | "extracting" | "done"
  urls?: string[]
}

export default function CrawlProgress({ stage, urls = [] }: CrawlProgressProps) {
  if (stage === "idle") return null

  return (
    <div className="border rounded p-3 bg-gray-50 text-sm">
      <strong>Status:</strong>{" "}
      {stage === "searching" && "Searching the web…"}
      {stage === "extracting" && "Extracting data from sources…"}
      {stage === "done" && "Extraction complete"}

      {urls.length > 0 && (
        <ul className="mt-2 list-disc list-inside">
          {urls.slice(0, 5).map((u) => (
            <li key={u} className="truncate text-blue-600">
              {u}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

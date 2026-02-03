// src/components/DataTable.tsx

interface DataTableProps {
  rows: Record<string, any>[]
}

export default function DataTable({ rows }: DataTableProps) {
  if (!rows || rows.length === 0) return null

  const columns = Object.keys(rows[0])

  return (
    <div className="overflow-x-auto mt-4">
      <table className="min-w-full border border-gray-300 text-sm">
        <thead className="bg-gray-100">
          <tr>
            {columns.map((c) => (
              <th
                key={c}
                className="border px-3 py-2 text-left font-semibold"
              >
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="hover:bg-gray-50">
              {columns.map((c) => (
                <td key={c} className="border px-3 py-2">
                  {String(row[c])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

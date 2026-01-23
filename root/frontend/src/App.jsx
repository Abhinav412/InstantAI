import { useEffect, useState } from "react"

const API_BASE = "http://127.0.0.1:8000"

export default function App() {
  const [datasetId, setDatasetId] = useState("")
  const [dataset, setDataset] = useState(null)
  const [uploadedFile, setUploadedFile] = useState(null)

  const [kpi, setKpi] = useState("")
  const [entityColumn, setEntityColumn] = useState("")
  const [ranking, setRanking] = useState([])
  const [displayLimit, setDisplayLimit] = useState(10)

  const [chatInput, setChatInput] = useState("")
  const [chatResponse, setChatResponse] = useState("")
  const [chatTableData, setChatTableData] = useState(null)

  // Handle file upload
  async function handleFileUpload(event) {
    const file = event.target.files[0]
    if (!file) return

    // Check if it's a supported file
    if (!file.name.match(/\.(csv|xlsx|json)$/)) {
      alert('Please upload a CSV, XLSX, or JSON file')
      return
    }

    setUploadedFile(file)

    // Create FormData and upload
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
      })

      if (!res.ok) {
        alert(`Upload failed: ${res.status} ${res.statusText}`)
        return
      }

      const data = await res.json()
      console.log('Upload response:', data)

      // Check the response format from your backend
      if (data.status === 'OK' && data.dataset_id) {
        setDatasetId(data.dataset_id)
        // Automatically load the dataset
        await loadDatasetById(data.dataset_id)
      } else if (data.status === 'ERROR') {
        alert(`Upload error: ${data.reason}`)
      }
    } catch (error) {
      console.error('Upload error:', error)
      alert(`Upload error: ${error.message}`)
    }
  }

  async function loadDataset() {
    const res = await fetch(`${API_BASE}/dataset/${datasetId}`)
    const data = await res.json()
    setDataset(data)
  }

  async function loadDatasetById(id) {
    const res = await fetch(`${API_BASE}/dataset/${id}`)
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

  // Parse patient data from text response
  const parsePatientData = (text) => {
    try {
      const patientMatches = text.match(/\{[^}]*'patient_id'[^}]*\}/g)
      
      if (!patientMatches || patientMatches.length === 0) {
        return null
      }

      const patients = patientMatches.map(match => {
        const patient = {}
        const pairs = match.match(/'(\w+)':\s*'?([^',}]+)'?/g)
        
        if (pairs) {
          pairs.forEach(pair => {
            const cleanPair = pair.replace(/'/g, '')
            const [key, ...valueParts] = cleanPair.split(':')
            const value = valueParts.join(':').trim()
            patient[key] = value
          })
        }
        
        return patient
      })

      return patients.length > 0 ? patients : null
    } catch (error) {
      console.error("Error parsing patient data:", error)
      return null
    }
  }

  async function runChat() {
    if (!datasetId || !chatInput) {
      alert("Please upload a dataset and enter a question")
      return
    }

    try {
      const params = new URLSearchParams({
        dataset_id: datasetId,
        user_query: chatInput,
      })

      console.log("Sending request to:", `${API_BASE}/chat?${params}`)
      const res = await fetch(`${API_BASE}/chat?${params}`, { method: "POST" })
      
      if (!res.ok) {
        setChatResponse(`Error: ${res.status} ${res.statusText}`)
        setChatTableData(null)
        return
      }

      const data = await res.json()
      console.log("Chat response received:", data)
      
      // Handle different response formats
      let responseText = ""
      if (data.response) {
        responseText = data.response
      } else if (data.answer) {
        responseText = data.answer
      } else if (data.result) {
        responseText = data.result
      } else {
        responseText = JSON.stringify(data, null, 2)
      }
      
      // Try to parse as table data
      const parsedData = parsePatientData(responseText)
      
      if (parsedData) {
        setChatTableData(parsedData)
        setChatResponse("")
      } else {
        setChatResponse(responseText)
        setChatTableData(null)
      }
    } catch (error) {
      console.error("Chat error:", error)
      setChatResponse(`Error: ${error.message}`)
      setChatTableData(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">Agentic Analytics Dashboard</h1>
          <p className="text-slate-400">Advanced Dataset Analysis & Ranking Engine</p>
        </header>

        {/* Dataset Section */}
        <section className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-2xl font-bold mb-4 text-blue-400">📊 Dataset</h2>
          <div className="space-y-3">
            {/* File Upload */}
            <div className="border-2 border-dashed border-slate-600 rounded-lg p-6 text-center hover:border-blue-500 transition">
              <input
                type="file"
                accept=".csv,.xlsx,.json"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
              />
              <label 
                htmlFor="file-upload" 
                className="cursor-pointer flex flex-col items-center gap-2"
              >
                <svg 
                  className="w-12 h-12 text-slate-400" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" 
                  />
                </svg>
                <span className="text-slate-300 font-semibold">
                  {uploadedFile ? uploadedFile.name : 'Click to upload file'}
                </span>
                <span className="text-slate-500 text-sm">CSV, XLSX, or JSON</span>
              </label>
            </div>

            {/* Or divider */}
            <div className="flex items-center gap-3">
              <div className="flex-1 h-px bg-slate-600"></div>
              <span className="text-slate-500 text-sm">OR</span>
              <div className="flex-1 h-px bg-slate-600"></div>
            </div>

            {/* Manual Dataset ID Input */}
            <div className="flex gap-2">
              <input
                className="flex-1 p-3 bg-slate-700 rounded text-white placeholder-slate-400 border border-slate-600 focus:border-blue-500 focus:outline-none"
                placeholder="Enter Dataset ID manually"
                value={datasetId}
                onChange={(e) => setDatasetId(e.target.value)}
              />
              <button 
                onClick={loadDataset} 
                className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded font-semibold transition"
              >
                Load
              </button>
            </div>

            {dataset && (
              <div className="bg-slate-700 p-4 rounded mt-4">
                <p className="text-slate-300"><strong>Dataset ID:</strong> {datasetId.substring(0, 20)}...</p>
                <p className="text-slate-300"><strong>Columns:</strong> {dataset.profile.fields.column_count}</p>
                <p className="text-slate-300"><strong>Rows:</strong> {dataset.profile.fields.row_count}</p>
              </div>
            )}
          </div>
        </section>

        {/* Ranking Section */}
        <section className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-2xl font-bold mb-4 text-green-400">🏆 Ranking Results</h2>
          <div className="space-y-3 mb-4">
            <input
              className="p-3 bg-slate-700 rounded w-full text-white placeholder-slate-400 border border-slate-600 focus:border-green-500 focus:outline-none"
              placeholder="KPI column (e.g., treatment_cost)"
              value={kpi}
              onChange={(e) => setKpi(e.target.value)}
            />

            <input
              className="p-3 bg-slate-700 rounded w-full text-white placeholder-slate-400 border border-slate-600 focus:border-green-500 focus:outline-none"
              placeholder="Entity column (e.g., patient_id)"
              value={entityColumn}
              onChange={(e) => setEntityColumn(e.target.value)}
            />

            <button onClick={runRanking} className="w-full bg-green-600 hover:bg-green-700 px-4 py-2 rounded font-semibold transition">
              Run Ranking
            </button>
          </div>

        {ranking.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-700 border-b border-slate-600">
                    <th className="px-4 py-2 text-left">Rank</th>
                    <th className="px-4 py-2 text-left">{entityColumn || 'Entity'}</th>
                    <th className="px-4 py-2 text-right">{kpi || 'Value'}</th>
                  </tr>
                </thead>
                <tbody>
                  {ranking.slice(0, displayLimit).map((r, idx) => (
                    <tr key={idx} className="border-b border-slate-700 hover:bg-slate-700 transition">
                      <td className="px-4 py-3 font-bold text-green-400">#{r.rank}</td>
                      <td className="px-4 py-3">{r.entity}</td>
                      <td className="px-4 py-3 text-right font-semibold">{typeof r.value === 'number' ? r.value.toFixed(2) : r.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="mt-4 flex justify-center items-center gap-4">
                <p className="text-slate-400 text-sm">
                  Showing {displayLimit} of {ranking.length} results
                </p>
                {displayLimit < ranking.length && (
                  <button 
                    onClick={() => setDisplayLimit(displayLimit + 10)}
                    className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded font-semibold transition"
                  >
                    Load More
                  </button>
                )}
                {displayLimit >= ranking.length && ranking.length > 10 && (
                  <button 
                    onClick={() => setDisplayLimit(10)}
                    className="bg-slate-600 hover:bg-slate-700 px-6 py-2 rounded font-semibold transition"
                  >
                    Show Less
                  </button>
                )}
              </div>
            </div>
          )}
        </section>

        {/* Chat Section */}
        <section className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-2xl font-bold mb-4 text-purple-400">💬 Chat with Dataset</h2>
          <div className="space-y-3">
            <textarea
              className="p-3 bg-slate-700 rounded w-full text-white placeholder-slate-400 border border-slate-600 focus:border-purple-500 focus:outline-none resize-none"
              rows={4}
              placeholder="Ask a question about your dataset (e.g., 'What is the average treatment cost?' or 'Show me top 10 patients by cost')"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
            />

            <button onClick={runChat} className="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded font-semibold transition">
              Ask
            </button>

            {/* Table Display */}
            {chatTableData && (
              <div className="bg-slate-700 rounded mt-4 border-l-4 border-purple-500 overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-600">
                      <th className="px-4 py-3 text-left text-purple-300">#</th>
                      <th className="px-4 py-3 text-left text-purple-300">Patient ID</th>
                      <th className="px-4 py-3 text-left text-purple-300">Age</th>
                      <th className="px-4 py-3 text-left text-purple-300">Gender</th>
                      <th className="px-4 py-3 text-left text-purple-300">Admission Type</th>
                      <th className="px-4 py-3 text-left text-purple-300">Diagnosis</th>
                      <th className="px-4 py-3 text-right text-purple-300">Treatment Cost</th>
                      <th className="px-4 py-3 text-left text-purple-300">Length of Stay</th>
                      <th className="px-4 py-3 text-left text-purple-300">Discharge Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {chatTableData.map((patient, idx) => (
                      <tr key={idx} className="border-b border-slate-600 hover:bg-slate-600">
                        <td className="px-4 py-3 font-bold text-purple-400">{idx + 1}</td>
                        <td className="px-4 py-3">{patient.patient_id}</td>
                        <td className="px-4 py-3">{patient.age}</td>
                        <td className="px-4 py-3">{patient.gender}</td>
                        <td className="px-4 py-3">{patient.admission_type}</td>
                        <td className="px-4 py-3">{patient.diagnosis}</td>
                        <td className="px-4 py-3 text-right font-semibold">${patient.treatment_cost}</td>
                        <td className="px-4 py-3">{patient.length_of_stay_days} days</td>
                        <td className="px-4 py-3">{patient.discharge_status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Text Display (fallback) */}
            {chatResponse && !chatTableData && (
              <div className="bg-slate-700 p-4 rounded mt-4 border-l-4 border-purple-500">
                <p className="text-slate-200 whitespace-pre-wrap leading-relaxed">{chatResponse}</p>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Topbar from '../components/Topbar'
import { Loading, ErrorBox } from '../components/States'
import { listPumps } from '../lib/api'

export default function PumpList() {
  const [pumps, setPumps] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listPumps()
      .then(setPumps)
      .catch((e) => setError(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <Topbar title="Pumps" subtitle="Select a pump to inspect telemetry & predictions" />
      <div className="p-6">
        {loading && <Loading />}
        {error && <ErrorBox message={error} />}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {pumps.map((id) => (
            <Link
              key={id}
              to={`/pumps/${id}`}
              className="card p-4 hover:border-industrial-accent/50 hover:shadow-glow transition-all text-center"
            >
              <div className="text-2xl mb-1">⛽</div>
              <div className="font-mono text-sm">{id}</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}

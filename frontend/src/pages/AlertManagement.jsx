import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Topbar from '../components/Topbar'
import AlertBadge from '../components/AlertBadge'
import { Loading, ErrorBox } from '../components/States'
import { getAlerts } from '../lib/api'

export default function AlertManagement() {
  const [alerts, setAlerts] = useState([])
  const [filter, setFilter] = useState('All')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAlerts()
      .then(setAlerts)
      .catch((e) => setError(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [])

  const filtered = alerts.filter((a) => filter === 'All' || a.alert_level === filter)
  const counts = {
    Critical: alerts.filter((a) => a.alert_level === 'Critical').length,
    Warning: alerts.filter((a) => a.alert_level === 'Warning').length,
  }

  return (
    <div>
      <Topbar title="Alert Management" subtitle="Critical & warning pumps with maintenance recommendations" />
      <div className="p-6 space-y-5">
        {loading && <Loading />}
        {error && <ErrorBox message={error} />}
        {!loading && !error && (
          <>
            <div className="flex gap-2">
              {['All', 'Critical', 'Warning', 'Normal'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1.5 rounded-xl text-sm border transition-all ${
                    filter === f
                      ? 'bg-industrial-accent/15 border-industrial-accent/40 text-industrial-cyan'
                      : 'border-industrial-border text-industrial-muted hover:text-industrial-text'
                  }`}
                >
                  {f}
                  {counts[f] !== undefined && ` (${counts[f]})`}
                </button>
              ))}
            </div>

            <div className="card overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-industrial-panel text-industrial-muted text-[11px] uppercase tracking-wider">
                  <tr>
                    <th className="text-left px-4 py-3">Pump</th>
                    <th className="text-left px-4 py-3">Level</th>
                    <th className="text-right px-4 py-3">P(fail)</th>
                    <th className="text-right px-4 py-3">RUL (d)</th>
                    <th className="text-right px-4 py-3">Anomaly</th>
                    <th className="text-left px-4 py-3">Recommendation</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((a) => (
                    <tr key={a.pump_id} className="border-t border-industrial-border hover:bg-white/5">
                      <td className="px-4 py-3 font-mono">
                        <Link to={`/pumps/${a.pump_id}`} className="text-industrial-cyan hover:underline">
                          {a.pump_id}
                        </Link>
                      </td>
                      <td className="px-4 py-3"><AlertBadge level={a.alert_level} /></td>
                      <td className="px-4 py-3 text-right">{((a.failure_probability ?? 0) * 100).toFixed(0)}%</td>
                      <td className="px-4 py-3 text-right">{(a.rul_days ?? 0).toFixed(1)}</td>
                      <td className="px-4 py-3 text-right">{((a.anomaly_score ?? 0) * 100).toFixed(0)}%</td>
                      <td className="px-4 py-3 text-industrial-muted">{a.recommendation}</td>
                    </tr>
                  ))}
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-industrial-muted">
                        No alerts for this filter.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

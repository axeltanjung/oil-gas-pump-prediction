import { useEffect, useState } from 'react'
import Topbar from '../components/Topbar'
import KpiCard from '../components/KpiCard'
import RiskHeatmap from '../components/RiskHeatmap'
import ChartCard from '../components/ChartCard'
import { Loading, ErrorBox } from '../components/States'
import { getSummary, getRiskHeatmap } from '../lib/api'

export default function Overview() {
  const [summary, setSummary] = useState(null)
  const [heatmap, setHeatmap] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getSummary(), getRiskHeatmap()])
      .then(([s, h]) => {
        setSummary(s)
        setHeatmap(h)
      })
      .catch((e) => setError(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [])

  const rulTrend = heatmap.map((c) => ({ timestamp: c.pump_id, value: c.rul_days }))

  return (
    <div>
      <Topbar title="Fleet Overview" subtitle="Real-time predictive maintenance dashboard" />
      <div className="p-6 space-y-6">
        {loading && <Loading label="Loading fleet summary…" />}
        {error && <ErrorBox message={error} />}
        {summary && (
          <>
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
              <KpiCard label="Total Pumps" value={summary.total_pumps} accent="cyan" />
              <KpiCard label="Active Alerts" value={summary.active_alerts} accent="amber" />
              <KpiCard label="High Risk" value={summary.high_risk_pumps} accent="red" hint="P(fail) ≥ 50%" />
              <KpiCard
                label="Avg Health"
                value={(summary.average_health_score * 100).toFixed(0)}
                unit="%"
                accent="green"
              />
              <KpiCard label="Avg RUL" value={summary.average_rul_days.toFixed(1)} unit="days" accent="cyan" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <RiskHeatmap cells={heatmap} />
              <ChartCard
                title="RUL by Pump (days)"
                data={rulTrend}
                color="#22d3ee"
                area
                unit="days"
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <KpiCard label="Critical Pumps" value={summary.critical_pumps} accent="red" />
              <KpiCard label="Warning Pumps" value={summary.warning_pumps} accent="amber" />
              <KpiCard
                label="Healthy Pumps"
                value={summary.total_pumps - summary.critical_pumps - summary.warning_pumps}
                accent="green"
              />
            </div>
          </>
        )}
      </div>
    </div>
  )
}

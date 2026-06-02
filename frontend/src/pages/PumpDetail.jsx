import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import Topbar from '../components/Topbar'
import ChartCard from '../components/ChartCard'
import Gauge from '../components/Gauge'
import KpiCard from '../components/KpiCard'
import AlertBadge from '../components/AlertBadge'
import { Loading, ErrorBox } from '../components/States'
import { getPump, reportUrl } from '../lib/api'

const SENSORS = [
  { key: 'pressure', title: 'Pressure', color: '#22d3ee', unit: 'bar' },
  { key: 'vibration', title: 'Vibration', color: '#f59e0b', unit: 'mm/s' },
  { key: 'temperature', title: 'Temperature', color: '#ef4444', unit: '°C' },
  { key: 'rpm', title: 'RPM', color: '#0ea5e9', unit: 'rpm' },
  { key: 'flow_rate', title: 'Flow Rate', color: '#10b981', unit: 'm³/h' },
  { key: 'power_consumption', title: 'Power', color: '#a78bfa', unit: 'kW' },
]

export default function PumpDetail() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getPump(id)
      .then(setData)
      .catch((e) => setError(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [id])

  return (
    <div>
      <Topbar title={`Pump ${id}`} subtitle="Sensor trends, health & failure predictions" />
      <div className="p-6 space-y-6">
        {loading && <Loading />}
        {error && <ErrorBox message={error} />}
        {data && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
              <div className="card p-5 flex flex-col items-center justify-center">
                <Gauge value={data.health_score ?? 0} label="Health" />
                <div className="mt-2">
                  <AlertBadge level={data.alert_level} />
                </div>
              </div>
              <KpiCard
                label="Failure Probability"
                value={((data.failure_probability ?? 0) * 100).toFixed(1)}
                unit="%"
                accent={data.failure_probability > 0.5 ? 'red' : 'green'}
              />
              <KpiCard label="Remaining Useful Life" value={(data.rul_days ?? 0).toFixed(1)} unit="days" accent="cyan" />
              <KpiCard
                label="Anomaly Score"
                value={((data.anomaly_score ?? 0) * 100).toFixed(0)}
                unit="%"
                accent={data.anomaly_score > 0.5 ? 'amber' : 'green'}
              />
            </div>

            <div className="flex justify-end">
              <a
                href={reportUrl(id)}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 rounded-xl text-sm bg-industrial-accent/15 border border-industrial-accent/40 text-industrial-cyan hover:shadow-glow transition-all"
              >
                ⬇ Download Maintenance Report (PDF)
              </a>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {SENSORS.map((s) => (
                <ChartCard
                  key={s.key}
                  title={s.title}
                  data={data.trends[s.key] || []}
                  color={s.color}
                  unit={s.unit}
                />
              ))}
            </div>

            <ChartCard
              title="Anomaly Timeline"
              data={data.anomaly_timeline || []}
              color="#ef4444"
              area
              unit="score"
            />
          </>
        )}
      </div>
    </div>
  )
}

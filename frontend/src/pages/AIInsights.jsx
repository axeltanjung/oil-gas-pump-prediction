import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import Topbar from '../components/Topbar'
import KpiCard from '../components/KpiCard'
import { Loading, ErrorBox } from '../components/States'
import { getDrivers, getFeatureImportance, getForecastMetrics } from '../lib/api'

const tooltipStyle = {
  background: '#111722',
  border: '1px solid #1f2937',
  borderRadius: 8,
  fontSize: 12,
}

function DriverChart({ title, data, valueKey, color }) {
  return (
    <div className="card p-4 animate-fade-in">
      <h3 className="text-sm font-medium mb-3">{title}</h3>
      <ResponsiveContainer width="100%" height={Math.max(220, data.length * 26)}>
        <BarChart data={data} layout="vertical" margin={{ left: 30, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" horizontal={false} />
          <XAxis type="number" tick={{ fill: '#64748b', fontSize: 10 }} />
          <YAxis
            type="category"
            dataKey="feature"
            tick={{ fill: '#94a3b8', fontSize: 10 }}
            width={140}
          />
          <Tooltip contentStyle={tooltipStyle} cursor={{ fill: '#ffffff08' }} />
          <Bar dataKey={valueKey} radius={[0, 4, 4, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={color} fillOpacity={1 - i * 0.03} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default function AIInsights() {
  const [drivers, setDrivers] = useState([])
  const [importance, setImportance] = useState({ failure: [], rul: [] })
  const [forecast, setForecast] = useState({})
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getDrivers(), getFeatureImportance(), getForecastMetrics()])
      .then(([d, fi, fm]) => {
        setDrivers(d)
        setImportance(fi)
        setForecast(fm || {})
      })
      .catch((e) => setError(e.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [])

  const driverKey = drivers[0]?.mean_abs_shap !== undefined ? 'mean_abs_shap' : 'importance'

  return (
    <div>
      <Topbar title="AI Insights" subtitle="Explainability, failure drivers & model performance" />
      <div className="p-6 space-y-6">
        {loading && <Loading />}
        {error && <ErrorBox message={error} />}
        {!loading && (
          <>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <KpiCard label="Top Driver" value={drivers[0]?.feature || '—'} accent="cyan" />
              <KpiCard label="LSTM RMSE" value={(forecast.rmse ?? 0).toFixed(3)} accent="amber" hint="health forecast" />
              <KpiCard label="LSTM MAE" value={(forecast.mae ?? 0).toFixed(3)} accent="amber" />
              <KpiCard label="Drivers Tracked" value={drivers.length} accent="green" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <DriverChart
                title={driverKey === 'mean_abs_shap' ? 'SHAP — Top Failure Drivers' : 'Top Failure Drivers (importance)'}
                data={drivers}
                valueKey={driverKey}
                color="#22d3ee"
              />
              <DriverChart
                title="RUL Model — Feature Importance"
                data={importance.rul || []}
                valueKey="importance"
                color="#10b981"
              />
            </div>

            <DriverChart
              title="Failure Model — Feature Importance"
              data={importance.failure || []}
              valueKey="importance"
              color="#0ea5e9"
            />
          </>
        )}
      </div>
    </div>
  )
}

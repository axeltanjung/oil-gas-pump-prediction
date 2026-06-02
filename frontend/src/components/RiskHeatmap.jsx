import { Link } from 'react-router-dom'
import { ALERT_COLORS } from '../lib/api'

// Grid of pump risk cells colored by alert level + failure probability.
export default function RiskHeatmap({ cells = [] }) {
  return (
    <div className="card p-4 animate-fade-in">
      <h3 className="text-sm font-medium mb-3">Fleet Risk Heatmap</h3>
      <div className="grid grid-cols-5 sm:grid-cols-8 gap-2">
        {cells.map((c) => {
          const color = ALERT_COLORS[c.alert_level] || '#10b981'
          const intensity = 0.2 + 0.8 * Math.min(1, c.failure_proba)
          return (
            <Link
              key={c.pump_id}
              to={`/pumps/${c.pump_id}`}
              title={`${c.pump_id} · P(fail)=${(c.failure_proba * 100).toFixed(0)}% · RUL=${c.rul_days}d`}
              className="aspect-square rounded-lg border flex items-center justify-center text-[9px] font-mono transition-transform hover:scale-105"
              style={{
                background: `${color}${Math.round(intensity * 255).toString(16).padStart(2, '0')}`,
                borderColor: `${color}66`,
                color: '#0a0e14',
              }}
            >
              {c.pump_id.replace('PUMP-', '')}
            </Link>
          )
        })}
      </div>
      <div className="flex gap-4 mt-3 text-[11px] text-industrial-muted">
        {Object.entries(ALERT_COLORS).map(([k, v]) => (
          <span key={k} className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded" style={{ background: v }} /> {k}
          </span>
        ))}
      </div>
    </div>
  )
}

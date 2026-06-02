import { ALERT_COLORS } from '../lib/api'

export default function AlertBadge({ level }) {
  const color = ALERT_COLORS[level] || '#94a3b8'
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border"
      style={{ color, borderColor: `${color}55`, background: `${color}15` }}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ background: color }} />
      {level}
    </span>
  )
}

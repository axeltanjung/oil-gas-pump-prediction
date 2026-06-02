// Radial health gauge (0..1). Uses SVG arc.
export default function Gauge({ value = 0, label = 'Health', size = 160 }) {
  const pct = Math.max(0, Math.min(1, value))
  const radius = size / 2 - 14
  const circumference = Math.PI * radius // half circle
  const offset = circumference * (1 - pct)

  const color = pct > 0.66 ? '#10b981' : pct > 0.33 ? '#f59e0b' : '#ef4444'

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size / 2 + 16}>
        <path
          d={`M 12 ${size / 2} A ${radius} ${radius} 0 0 1 ${size - 12} ${size / 2}`}
          fill="none"
          stroke="#1f2937"
          strokeWidth="12"
          strokeLinecap="round"
        />
        <path
          d={`M 12 ${size / 2} A ${radius} ${radius} 0 0 1 ${size - 12} ${size / 2}`}
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>
      <div className="-mt-8 text-center">
        <div className="text-2xl font-bold" style={{ color }}>
          {(pct * 100).toFixed(0)}%
        </div>
        <div className="text-[11px] uppercase tracking-widest text-industrial-muted">{label}</div>
      </div>
    </div>
  )
}

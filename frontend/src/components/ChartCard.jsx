import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function fmtTime(ts) {
  if (!ts) return ''
  return String(ts).slice(5, 16).replace('T', ' ')
}

const tooltipStyle = {
  background: '#111722',
  border: '1px solid #1f2937',
  borderRadius: 8,
  fontSize: 12,
  color: '#e5e7eb',
}

export default function ChartCard({ title, data, dataKey = 'value', color = '#22d3ee', area = false, unit = '' }) {
  const Chart = area ? AreaChart : LineChart
  return (
    <div className="card p-4 animate-fade-in">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-industrial-text">{title}</h3>
        {unit && <span className="text-[11px] text-industrial-muted">{unit}</span>}
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <Chart data={data} margin={{ top: 5, right: 10, left: -18, bottom: 0 }}>
          <defs>
            <linearGradient id={`grad-${title}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.4} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis dataKey="timestamp" tickFormatter={fmtTime} tick={{ fill: '#64748b', fontSize: 10 }} minTickGap={40} />
          <YAxis tick={{ fill: '#64748b', fontSize: 10 }} width={40} domain={['auto', 'auto']} />
          <Tooltip contentStyle={tooltipStyle} labelFormatter={fmtTime} />
          {area ? (
            <Area type="monotone" dataKey={dataKey} stroke={color} fill={`url(#grad-${title})`} strokeWidth={2} />
          ) : (
            <Line type="monotone" dataKey={dataKey} stroke={color} dot={false} strokeWidth={2} />
          )}
        </Chart>
      </ResponsiveContainer>
    </div>
  )
}

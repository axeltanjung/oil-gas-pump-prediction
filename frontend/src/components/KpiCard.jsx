export default function KpiCard({ label, value, unit, accent = 'cyan', hint }) {
  const accents = {
    cyan: 'text-industrial-cyan border-industrial-accent/30 shadow-glow',
    green: 'text-industrial-green border-industrial-green/30',
    amber: 'text-industrial-amber border-industrial-amber/30',
    red: 'text-industrial-red border-industrial-red/30 shadow-glow-red',
  }
  return (
    <div
      className={`card p-5 animate-fade-in border ${accents[accent]} bg-gradient-to-br from-industrial-card to-industrial-panel`}
    >
      <div className="text-[11px] uppercase tracking-widest text-industrial-muted">{label}</div>
      <div className="mt-2 flex items-end gap-1">
        <span className={`text-3xl font-bold ${accents[accent].split(' ')[0]}`}>{value}</span>
        {unit && <span className="text-sm text-industrial-muted mb-1">{unit}</span>}
      </div>
      {hint && <div className="mt-1 text-[11px] text-industrial-muted">{hint}</div>}
    </div>
  )
}

export default function Topbar({ title, subtitle }) {
  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-industrial-border bg-industrial-panel/60 backdrop-blur">
      <div>
        <h1 className="text-lg font-semibold tracking-wide">{title}</h1>
        {subtitle && <p className="text-xs text-industrial-muted mt-0.5">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-2 text-xs text-industrial-muted">
        <span className="w-2 h-2 rounded-full bg-industrial-green animate-pulse-slow" />
        Live · Batch Mode
      </div>
    </header>
  )
}

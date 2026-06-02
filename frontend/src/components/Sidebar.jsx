import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Overview', icon: '▦' },
  { to: '/pumps', label: 'Pump Detail', icon: '⛽' },
  { to: '/insights', label: 'AI Insights', icon: '✦' },
  { to: '/alerts', label: 'Alerts', icon: '⚠' },
]

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 bg-industrial-panel border-r border-industrial-border flex flex-col">
      <div className="px-5 py-6 border-b border-industrial-border">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-industrial-accent/20 border border-industrial-accent/40 flex items-center justify-center text-industrial-cyan text-lg shadow-glow">
            ◉
          </div>
          <div>
            <div className="font-semibold tracking-wide text-sm">PUMP AI</div>
            <div className="text-[10px] text-industrial-muted uppercase tracking-widest">
              Predictive Maintenance
            </div>
          </div>
        </div>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all ${
                isActive
                  ? 'bg-industrial-accent/15 text-industrial-cyan border border-industrial-accent/30 shadow-glow'
                  : 'text-industrial-muted hover:bg-white/5 hover:text-industrial-text border border-transparent'
              }`
            }
          >
            <span className="text-base">{l.icon}</span>
            {l.label}
          </NavLink>
        ))}
      </nav>
      <div className="px-5 py-4 border-t border-industrial-border text-[10px] text-industrial-muted">
        Oil &amp; Gas · v1.0.0
      </div>
    </aside>
  )
}

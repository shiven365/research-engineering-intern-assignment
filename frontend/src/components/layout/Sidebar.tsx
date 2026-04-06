import { Layers, LayoutDashboard, MessageSquare, Network, TrendingUp } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { icon: LayoutDashboard, label: 'Overview', path: '/' },
  { icon: TrendingUp, label: 'Timeline', path: '/timeline' },
  { icon: Network, label: 'Network', path: '/network' },
  { icon: Layers, label: 'Topics', path: '/clusters' },
  { icon: MessageSquare, label: 'Intelligence', path: '/chat' },
]

export default function Sidebar() {
  return (
    <aside
      style={{
        width: 240,
        background: 'linear-gradient(180deg, rgba(13,22,40,0.98) 0%, rgba(10,18,32,0.98) 100%)',
        borderRight: '1px solid var(--border)',
        minHeight: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        padding: 16,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <div style={{ marginBottom: 24 }}>
        <div style={{ fontFamily: 'var(--font-display)', fontSize: 20, letterSpacing: 0.5, color: 'var(--text-primary)' }}>
          <span style={{ color: 'var(--accent-primary)' }}>◈</span> NarrativeScope
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Narrative Intelligence Console</div>
      </div>

      <nav style={{ display: 'grid', gap: 6 }}>
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '10px 12px',
                border: `1px solid ${isActive ? 'var(--border-bright)' : 'transparent'}`,
                borderLeft: `3px solid ${isActive ? 'var(--accent-primary)' : 'transparent'}`,
                borderRadius: 8,
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                background: isActive ? 'linear-gradient(90deg, rgba(72,216,176,0.08), rgba(106,162,255,0.08))' : 'transparent',
              })}
            >
              <Icon size={16} />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      <div style={{ marginTop: 'auto', color: 'var(--text-muted)', fontSize: 12 }}>v1.0 · SimPPL</div>
    </aside>
  )
}

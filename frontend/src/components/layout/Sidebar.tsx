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
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-title">
          <span className="sidebar-brand-glyph">◈</span>
          <span className="sidebar-nav-text">NarrativeScope</span>
        </div>
        <div className="sidebar-brand-subtitle">Narrative Intelligence Console</div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `sidebar-link${isActive ? ' is-active' : ''}`}
            >
              <Icon size={16} />
              <span className="sidebar-nav-text">{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      <div className="sidebar-footer">v1.0 · SimPPL</div>
    </aside>
  )
}

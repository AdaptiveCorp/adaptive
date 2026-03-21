import { NavLink } from 'react-router-dom'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <header style={{
        height: 56,
        borderBottom: '1px solid rgba(22, 40, 64, 0.85)',
        background: 'rgba(6, 16, 28, 0.92)',
        backdropFilter: 'blur(14px)',
        WebkitBackdropFilter: 'blur(14px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}>
        <div className="max-w-7xl mx-auto px-5 h-full flex items-center gap-6">

          {/* Logo */}
          <NavLink to="/" className="flex items-center gap-2.5 no-underline select-none">
            <div style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: 'linear-gradient(140deg, #0EA5E9 0%, #0369A1 100%)',
              boxShadow: '0 0 16px rgba(14, 165, 233, 0.28)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}>
              <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
                <path d="M7.5 1.5L2 4.8V9C2 11.6 4.5 13.6 7.5 14.3C10.5 13.6 13 11.6 13 9V4.8L7.5 1.5Z"
                  fill="white" fillOpacity=".88"/>
                <path d="M5 7.8L6.8 9.6L10.5 6" stroke="white" strokeWidth="1.3"
                  strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontWeight: 600,
              fontSize: 15,
              letterSpacing: '-0.02em',
              color: '#E2E8F0',
            }}>
              <span style={{ color: '#38BDF8' }}>AD</span>aptive
            </span>
          </NavLink>

          {/* Separator */}
          <div style={{ width: 1, height: 20, background: 'rgba(22, 40, 64, 0.9)' }} />

          {/* Nav */}
          <nav className="flex gap-1">
            <NavLink to="/" end className={({ isActive }) =>
              isActive ? 'nav-item-active' : 'nav-item'
            }>
              Projets
            </NavLink>
          </nav>

          <div className="flex-1" />

          {/* Status indicator */}
          <div className="flex items-center gap-2">
            <span className="status-dot" style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: '#10B981',
              boxShadow: '0 0 7px rgba(16, 185, 129, 0.65)',
              display: 'block',
              flexShrink: 0,
            }} />
            <span style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: 10,
              color: '#475569',
              letterSpacing: '0.07em',
              textTransform: 'uppercase',
            }}>sys.online</span>
          </div>

        </div>
      </header>

      <main className="max-w-7xl w-full mx-auto px-5 py-7 flex-1">
        {children}
      </main>
    </div>
  )
}

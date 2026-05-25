import { NavLink } from 'react-router-dom'
import { ThemeSwitcher } from './ThemeSwitcher'
import { BackgroundLayer } from './BackgroundLayer'
import { useApiHealth } from '../hooks/useApiHealth'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const apiOnline = useApiHealth()
  return (
    <>
      <BackgroundLayer />
      <div className="min-h-screen flex flex-col" style={{ position: 'relative', zIndex: 2 }}>
        <header style={{
          height: 67,
          borderBottom: '1px solid var(--border-base)',
          background: 'var(--bg-header)',
          backdropFilter: 'blur(14px)',
          WebkitBackdropFilter: 'blur(14px)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          transition: 'background 0.2s ease, border-color 0.2s ease',
        }}>
          <div className="px-8 h-full flex items-center gap-6">

            {/* Logo */}
            <NavLink to="/" className="flex items-center gap-2.5 no-underline select-none">
              <div style={{
                width: 38,
                height: 38,
                borderRadius: 10,
                background: 'linear-gradient(140deg, var(--brand-500) 0%, var(--brand-700) 100%)',
                boxShadow: '0 0 16px rgba(var(--brand-500-rgb), 0.28)',
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
                fontSize: 18,
                letterSpacing: '-0.02em',
                color: 'var(--text-bright)',
              }}>
                <span style={{ color: 'var(--brand-300)' }}>AD</span>aptive
              </span>
            </NavLink>

            {/* Separator */}
            <div style={{ width: 1, height: 24, background: 'var(--border-sep)' }} />

            {/* Nav */}
            <nav className="flex gap-1">
              <NavLink to="/" end className={({ isActive }) =>
                isActive ? 'nav-item-active' : 'nav-item'
              }>
                Projets
              </NavLink>
              <NavLink to="/vm-templates" className={({ isActive }) =>
                isActive ? 'nav-item-active' : 'nav-item'
              }>
                Templates VM
              </NavLink>
            </nav>

            <div className="flex-1" />

            {/* Theme switcher + status */}
            <div className="flex items-center gap-3">
              <ThemeSwitcher />

              <div style={{ width: 1, height: 24, background: 'var(--border-sep)' }} />

              <div className="flex items-center gap-2">
                <span className={apiOnline ? 'status-dot' : undefined} style={{
                  width: 7,
                  height: 7,
                  borderRadius: '50%',
                  background: apiOnline ? '#10B981' : '#6B7280',
                  boxShadow: apiOnline ? '0 0 7px rgba(16, 185, 129, 0.65)' : 'none',
                  display: 'block',
                  flexShrink: 0,
                }} />
                <span style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: 12,
                  color: apiOnline ? 'var(--text-dim)' : '#6B7280',
                  letterSpacing: '0.07em',
                  textTransform: 'uppercase',
                }}>{apiOnline ? 'api.online' : 'api.offline'}</span>
              </div>
            </div>

          </div>
        </header>

        <main className="w-full px-8 py-7 flex-1">
          {children}
        </main>
      </div>
    </>
  )
}

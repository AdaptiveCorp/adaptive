import { Shield } from 'lucide-react'
import { NavLink } from 'react-router-dom'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <header className="bg-dark-800 border-b border-dark-600 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center gap-4">
          <NavLink to="/" className="flex items-center gap-2 font-semibold text-slate-100">
            <Shield className="w-5 h-5 text-brand-400" />
            <span>
              AD<span className="text-brand-400">aptive</span>
            </span>
          </NavLink>

          <nav className="flex items-center gap-1 ml-4 text-sm">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg transition ${
                  isActive
                    ? 'bg-brand-600/20 text-brand-400'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-dark-600'
                }`
              }
            >
              Projets
            </NavLink>
          </nav>
        </div>
      </header>

      {/* Page */}
      <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 flex-1">{children}</main>
    </div>
  )
}

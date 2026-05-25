import type { ReactNode } from 'react'

interface Tab { id: string; label: string; icon: ReactNode }
interface Props { tabs: Tab[]; active: string; onChange: (id: string) => void }

export function TabBar({ tabs, active, onChange }: Props) {
  return (
    <div style={{
      display: 'flex',
      borderBottom: '1px solid var(--border-base)',
      overflowX: 'auto',
      scrollbarWidth: 'none',
      gap: 2,
    }}>
      {tabs.map((tab) => {
        const on = active === tab.id
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '9px 16px',
              fontSize: 13,
              fontWeight: on ? 600 : 500,
              whiteSpace: 'nowrap',
              border: 'none',
              borderBottom: `2px solid ${on ? 'var(--brand-400)' : 'transparent'}`,
              marginBottom: -1,
              color: on ? 'var(--brand-300)' : 'var(--text-nav)',
              background: on ? 'rgba(var(--brand-500-rgb), 0.06)' : 'transparent',
              transition: 'all 0.15s ease',
              cursor: 'pointer',
              outline: 'none',
              fontFamily: 'inherit',
            }}
            onMouseEnter={e => {
              if (!on) {
                e.currentTarget.style.color = 'var(--text-body)'
                e.currentTarget.style.background = 'var(--bg-row-hover)'
              }
            }}
            onMouseLeave={e => {
              if (!on) {
                e.currentTarget.style.color = 'var(--text-nav)'
                e.currentTarget.style.background = 'transparent'
              }
            }}
          >
            <span style={{ color: on ? 'var(--brand-400)' : 'var(--text-dim)' }}>{tab.icon}</span>
            {tab.label}
          </button>
        )
      })}
    </div>
  )
}

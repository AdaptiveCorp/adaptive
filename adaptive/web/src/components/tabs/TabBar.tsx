import type { ReactNode } from 'react'

interface Tab { id: string; label: string; icon: ReactNode }
interface Props { tabs: Tab[]; active: string; onChange: (id: string) => void }

export function TabBar({ tabs, active, onChange }: Props) {
  return (
    <div style={{
      display: 'flex',
      borderBottom: '1px solid rgba(22, 40, 64, 0.8)',
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
              borderBottom: `2px solid ${on ? '#0EA5E9' : 'transparent'}`,
              marginBottom: -1,
              color: on ? '#38BDF8' : '#64748B',
              background: on ? 'rgba(14, 165, 233, 0.06)' : 'transparent',
              transition: 'all 0.15s ease',
              cursor: 'pointer',
              outline: 'none',
              fontFamily: 'inherit',
            }}
            onMouseEnter={e => {
              if (!on) {
                const el = e.currentTarget
                el.style.color = '#64748B'
                el.style.background = 'rgba(15, 32, 52, 0.4)'
              }
            }}
            onMouseLeave={e => {
              if (!on) {
                const el = e.currentTarget
                el.style.color = '#64748B'
                el.style.background = 'transparent'
              }
            }}
          >
            <span style={{ color: on ? '#38BDF8' : '#475569' }}>{tab.icon}</span>
            {tab.label}
          </button>
        )
      })}
    </div>
  )
}

import { X } from 'lucide-react'
import { useEffect } from 'react'

interface ModalProps {
  title: string
  onClose: () => void
  children: React.ReactNode
}

export function Modal({ title, onClose, children }: ModalProps) {
  useEffect(() => {
    const h = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', h)
    return () => window.removeEventListener('keydown', h)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{
        background: 'rgba(4, 10, 20, 0.75)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
      }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
    >
      <div style={{
        width: '100%',
        maxWidth: 448,
        background: 'rgba(10, 23, 40, 0.96)',
        border: '1px solid rgba(14, 165, 233, 0.15)',
        borderRadius: 12,
        overflow: 'hidden',
        boxShadow: '0 8px 40px rgba(0,0,0,0.7), 0 0 0 1px rgba(14, 165, 233, 0.08), 0 0 60px rgba(14, 165, 233, 0.04)',
        animation: 'fade-in-up 0.2s ease forwards',
      }}>
        {/* Title bar */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '14px 20px',
          borderBottom: '1px solid rgba(22, 40, 64, 0.8)',
          background: 'rgba(6, 16, 28, 0.6)',
        }}>
          <h2 style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontWeight: 600,
            fontSize: 13,
            color: '#CBD5E1',
            letterSpacing: '0.01em',
          }}>
            {title}
          </h2>
          <button
            onClick={onClose}
            style={{
              width: 26,
              height: 26,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: 6,
              border: 'none',
              background: 'transparent',
              color: '#334155',
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
            onMouseEnter={e => {
              const el = e.currentTarget
              el.style.color = '#94A3B8'
              el.style.background = 'rgba(22, 40, 64, 0.8)'
            }}
            onMouseLeave={e => {
              const el = e.currentTarget
              el.style.color = '#334155'
              el.style.background = 'transparent'
            }}
          >
            <X style={{ width: 14, height: 14 }} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '20px' }}>
          {children}
        </div>
      </div>
    </div>
  )
}

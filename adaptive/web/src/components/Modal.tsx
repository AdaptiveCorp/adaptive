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
        background: 'var(--bg-card)',
        border: '1px solid rgba(14, 165, 233, 0.15)',
        borderRadius: 12,
        overflow: 'hidden',
        boxShadow: '0 8px 40px rgba(0,0,0,0.55), 0 0 60px rgba(14, 165, 233, 0.04)',
        animation: 'fade-in-up 0.2s ease forwards',
      }}>
        {/* Title bar */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '14px 20px',
          borderBottom: '1px solid var(--border-base)',
          background: 'var(--bg-tbl-head)',
        }}>
          <h2 style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontWeight: 600,
            fontSize: 13,
            color: 'var(--text-body)',
            letterSpacing: '0.01em',
          }}>
            {title}
          </h2>
          <button
            onClick={onClose}
            className="row-del"
            style={{ width: 26, height: 26 }}
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

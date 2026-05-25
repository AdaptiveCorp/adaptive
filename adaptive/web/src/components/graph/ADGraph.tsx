import { useRef, useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import type { Forest, Domain, Server, User, Group } from '../../types'

export interface Props {
  projectId: number
  forests: Forest[]
  domains: Domain[]
  servers: Server[]
  users: User[]
  groups: Group[]
}

interface View { x: number; y: number; scale: number }

const C = {
  forest: '#22C55E',
  domain: '#60A5FA',
  server: '#818CF8',
  user:   '#FBBF24',
  group:  '#FB923C',
}

const LEGEND: { key: keyof typeof C; label: string }[] = [
  { key: 'forest', label: 'Forêt'       },
  { key: 'domain', label: 'Domaine'     },
  { key: 'server', label: 'Serveur'     },
  { key: 'user',   label: 'Utilisateur' },
  { key: 'group',  label: 'Groupe'      },
]

const MAX_CHIPS = 8

// ── Chip ─────────────────────────────────────────────────────────────────────

function Chip({
  label, color, badge, onClick,
}: {
  label: string
  color: string
  badge?: string
  onClick?: () => void
}) {
  return (
    <div
      onClick={onClick}
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 5,
        background: `${color}12`, border: `1px solid ${color}28`,
        borderRadius: 5, padding: '3px 8px 3px 5px',
        flexShrink: 0, cursor: onClick ? 'pointer' : 'default',
        transition: 'background 0.12s, border-color 0.12s',
      }}
      onMouseEnter={e => {
        if (onClick) {
          (e.currentTarget as HTMLElement).style.background = `${color}22`
          ;(e.currentTarget as HTMLElement).style.borderColor = `${color}55`
        }
      }}
      onMouseLeave={e => {
        if (onClick) {
          (e.currentTarget as HTMLElement).style.background = `${color}12`
          ;(e.currentTarget as HTMLElement).style.borderColor = `${color}28`
        }
      }}
    >
      <div style={{
        width: 2.5, height: 13, borderRadius: 2,
        background: color, opacity: 0.75, flexShrink: 0,
      }} />
      <span style={{
        fontFamily: "'Fira Code', monospace", fontSize: 11,
        color: 'var(--text-bright)', whiteSpace: 'nowrap',
      }}>
        {label}
      </span>
      {badge && (
        <span style={{
          fontFamily: "'IBM Plex Mono', monospace", fontSize: 8, fontWeight: 700,
          color: '#10B981', background: 'rgba(16,185,129,0.12)',
          border: '1px solid rgba(16,185,129,0.3)',
          borderRadius: 3, padding: '1px 4px', letterSpacing: '0.5px',
        }}>
          {badge}
        </span>
      )}
    </div>
  )
}

// ── Section inside a domain ───────────────────────────────────────────────────

function ItemSection({
  label, color, children,
}: {
  label: string; color: string; children: React.ReactNode
}) {
  return (
    <div>
      <div style={{
        fontFamily: "'IBM Plex Mono', monospace", fontSize: 8.5, fontWeight: 700,
        color, letterSpacing: '0.12em', textTransform: 'uppercase',
        marginBottom: 6, opacity: 0.65,
      }}>
        {label}
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
        {children}
      </div>
    </div>
  )
}

// ── Domain box ────────────────────────────────────────────────────────────────

function DomainBox({
  domain, servers, users, groups, onNavigate,
}: {
  domain: Domain
  servers: Server[]
  users: User[]
  groups: Group[]
  onNavigate: (tab: string) => void
}) {
  const dServers = servers.filter(s => s.domain_id === domain.id)
  const dUsers   = users.filter(u => u.domain_id === domain.id)
  const dGroups  = groups.filter(g => g.domain_id === domain.id)
  const empty    = dServers.length === 0 && dUsers.length === 0 && dGroups.length === 0

  return (
    <div style={{
      border: `1.5px solid ${C.domain}70`,
      borderRadius: 8,
      padding: '10px 14px 14px',
      background: `${C.domain}08`,
    }}>
      {/* Domain label */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 7, marginBottom: 12,
      }}>
        <span style={{
          fontFamily: "'IBM Plex Mono', monospace", fontSize: 8.5, fontWeight: 700,
          color: C.domain, letterSpacing: '0.12em', textTransform: 'uppercase', opacity: 0.5,
        }}>
          DOMAINE
        </span>
        <span style={{ width: 1, height: 10, background: C.domain, opacity: 0.2, flexShrink: 0 }} />
        <span style={{
          fontFamily: "'Fira Code', monospace", fontSize: 12, fontWeight: 500,
          color: C.domain, opacity: 0.85,
        }}>
          {domain.fqdn}
        </span>
      </div>

      {empty ? (
        <p style={{
          fontFamily: "'IBM Plex Mono', monospace", fontSize: 10,
          color: 'var(--text-dim)', opacity: 0.45,
        }}>
          domaine vide
        </p>
      ) : (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 14 }}>
          {dServers.length > 0 && (
            <ItemSection label="Serveurs" color={C.server}>
              {dServers.slice(0, MAX_CHIPS).map(s => (
                <Chip key={s.id} label={s.fqdn} color={C.server}
                  badge={s.is_dc ? 'DC' : undefined}
                  onClick={() => onNavigate('servers')} />
              ))}
              {dServers.length > MAX_CHIPS && (
                <Chip label={`+${dServers.length - MAX_CHIPS}`} color={C.server}
                  onClick={() => onNavigate('servers')} />
              )}
            </ItemSection>
          )}
          {dUsers.length > 0 && (
            <ItemSection label="Utilisateurs" color={C.user}>
              {dUsers.slice(0, MAX_CHIPS).map(u => (
                <Chip key={u.id} label={u.username} color={C.user}
                  onClick={() => onNavigate('users')} />
              ))}
              {dUsers.length > MAX_CHIPS && (
                <Chip label={`+${dUsers.length - MAX_CHIPS}`} color={C.user}
                  onClick={() => onNavigate('users')} />
              )}
            </ItemSection>
          )}
          {dGroups.length > 0 && (
            <ItemSection label="Groupes" color={C.group}>
              {dGroups.slice(0, MAX_CHIPS).map(g => (
                <Chip key={g.id} label={g.name} color={C.group}
                  onClick={() => onNavigate('groups')} />
              ))}
              {dGroups.length > MAX_CHIPS && (
                <Chip label={`+${dGroups.length - MAX_CHIPS}`} color={C.group}
                  onClick={() => onNavigate('groups')} />
              )}
            </ItemSection>
          )}
        </div>
      )}
    </div>
  )
}

// ── Forest box ────────────────────────────────────────────────────────────────

function ForestBox({
  forest, domains, servers, users, groups, onNavigate,
}: {
  forest: Forest
  domains: Domain[]
  servers: Server[]
  users: User[]
  groups: Group[]
  onNavigate: (tab: string) => void
}) {
  const fDomains = domains.filter(d => d.forest_id === forest.id)

  return (
    <div style={{
      border: `1.5px dashed ${C.forest}65`,
      borderRadius: 12,
      padding: '12px 16px 16px',
    }}>
      {/* Forest label */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 7, marginBottom: 12,
      }}>
        <span style={{
          fontFamily: "'IBM Plex Mono', monospace", fontSize: 8.5, fontWeight: 700,
          color: C.forest, letterSpacing: '0.12em', textTransform: 'uppercase', opacity: 0.5,
        }}>
          FORÊT
        </span>
        <span style={{ width: 1, height: 10, background: C.forest, opacity: 0.2, flexShrink: 0 }} />
        <span style={{
          fontFamily: "'Fira Code', monospace", fontSize: 12, fontWeight: 500,
          color: C.forest, opacity: 0.85,
        }}>
          {forest.fqdn}
        </span>
      </div>

      {fDomains.length === 0 ? (
        <p style={{
          fontFamily: "'IBM Plex Mono', monospace", fontSize: 10,
          color: 'var(--text-dim)', opacity: 0.45,
        }}>
          aucun domaine
        </p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'row', flexWrap: 'wrap', gap: 10 }}>
          {fDomains.map(d => (
            <DomainBox key={d.id} domain={d}
              servers={servers} users={users} groups={groups}
              onNavigate={onNavigate} />
          ))}
        </div>
      )}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

export function ADGraph({ projectId, forests, domains, servers, users, groups }: Props) {
  const navigate      = useNavigate()
  const containerRef  = useRef<HTMLDivElement>(null)
  const contentRef    = useRef<HTMLDivElement>(null)
  const [view, setView] = useState<View>({ x: 0, y: 0, scale: 0 })
  const dragging      = useRef(false)
  const hasDragged    = useRef(false)
  const lastMouse     = useRef({ x: 0, y: 0 })

  const fitView = useCallback(() => {
    const container = containerRef.current
    const content   = contentRef.current
    if (!container || !content || forests.length === 0) return
    const cW   = container.clientWidth
    const cH   = container.clientHeight
    const cntW = content.offsetWidth
    const cntH = content.offsetHeight
    if (!cntW || !cntH) return
    const pad = 32
    const s   = Math.min((cW - pad * 2) / cntW, (cH - pad * 2) / cntH)
    setView({ x: (cW - cntW * s) / 2, y: (cH - cntH * s) / 2, scale: s })
  }, [forests.length])

  useEffect(() => {
    const t = setTimeout(fitView, 60)
    return () => clearTimeout(t)
  }, [fitView])

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const onWheel = (e: WheelEvent) => {
      e.preventDefault()
      const factor = e.deltaY < 0 ? 1.12 : 1 / 1.12
      const rect   = el.getBoundingClientRect()
      const cx = e.clientX - rect.left
      const cy = e.clientY - rect.top
      setView(v => {
        const ns = Math.max(0.1, Math.min(3, v.scale * factor))
        const r  = ns / v.scale
        return { x: cx - r * (cx - v.x), y: cy - r * (cy - v.y), scale: ns }
      })
    }
    el.addEventListener('wheel', onWheel, { passive: false })
    return () => el.removeEventListener('wheel', onWheel)
  }, [])

  const onMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return
    dragging.current   = true
    hasDragged.current = false
    lastMouse.current  = { x: e.clientX, y: e.clientY }
    e.preventDefault()
  }
  const onMouseMove = (e: React.MouseEvent) => {
    if (!dragging.current) return
    const dx = e.clientX - lastMouse.current.x
    const dy = e.clientY - lastMouse.current.y
    if (Math.abs(dx) > 2 || Math.abs(dy) > 2) hasDragged.current = true
    lastMouse.current = { x: e.clientX, y: e.clientY }
    setView(v => ({ ...v, x: v.x + dx, y: v.y + dy }))
  }
  const onMouseUp = () => { dragging.current = false }

  const zoom = (factor: number) => {
    const el = containerRef.current
    if (!el) return
    const cx = el.clientWidth  / 2
    const cy = el.clientHeight / 2
    setView(v => {
      const ns = Math.max(0.1, Math.min(3, v.scale * factor))
      const r  = ns / v.scale
      return { x: cx - r * (cx - v.x), y: cy - r * (cy - v.y), scale: ns }
    })
  }

  const onNavigate = useCallback((tab: string) => {
    if (!hasDragged.current) navigate(`/projects/${projectId}?tab=${tab}`)
  }, [navigate, projectId])

  if (forests.length === 0) {
    return (
      <div style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', padding: '48px 24px', gap: 10,
      }}>
        <svg width={40} height={40} viewBox="0 0 24 24" fill="none" style={{ opacity: 0.2 }}>
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
            stroke="var(--text-muted)" strokeWidth={1.5}
            strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <p style={{
          fontFamily: "'IBM Plex Mono', monospace", fontSize: 11,
          color: 'var(--text-dim)', letterSpacing: '0.08em', textTransform: 'uppercase',
        }}>
          Créez des forêts, domaines et serveurs
        </p>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>

      {/* Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
          {LEGEND.map(({ key, label }) => (
            <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <div style={{
                width: 8, height: 8, borderRadius: 2,
                background: `${C[key]}22`, border: `1.5px solid ${C[key]}`,
              }} />
              <span style={{
                fontFamily: "'IBM Plex Mono', monospace", fontSize: 9,
                color: 'var(--text-dim)', letterSpacing: '0.1em', textTransform: 'uppercase',
              }}>
                {label}
              </span>
            </div>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          {([
            { label: '+', fn: () => zoom(1.25) },
            { label: '−', fn: () => zoom(1 / 1.25) },
            { label: '⊡', fn: fitView },
          ] as const).map(btn => (
            <button key={btn.label} onClick={btn.fn} style={{
              width: 26, height: 26, display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderRadius: 5, border: '1px solid var(--border-base)', background: 'var(--bg-input)',
              color: 'var(--text-muted)', fontSize: btn.label === '⊡' ? 14 : 16,
              cursor: 'pointer', fontFamily: 'monospace', lineHeight: 1,
            }}>
              {btn.label}
            </button>
          ))}
        </div>
      </div>

      {/* Viewport */}
      <div
        ref={containerRef}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
        style={{
          position: 'relative', height: 400, overflow: 'hidden',
          borderRadius: 8, border: '1px solid var(--border-base)',
          background: 'var(--bg-card)',
          cursor: dragging.current ? 'grabbing' : 'grab',
          userSelect: 'none',
        }}
      >
        <div style={{
          position: 'absolute',
          transform: `translate(${view.x}px, ${view.y}px) scale(${view.scale})`,
          transformOrigin: '0 0',
        }}>
          <div
            ref={contentRef}
            style={{ display: 'flex', flexDirection: 'column', gap: 16 }}
          >
            {forests.map(f => (
              <ForestBox
                key={f.id} forest={f}
                domains={domains} servers={servers} users={users} groups={groups}
                onNavigate={onNavigate}
              />
            ))}
          </div>
        </div>

        <div style={{
          position: 'absolute', bottom: 8, right: 10,
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 9, color: 'var(--text-dim)', letterSpacing: '0.08em',
        }}>
          {Math.round(view.scale * 100)}%
        </div>
      </div>
    </div>
  )
}

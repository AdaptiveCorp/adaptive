import { useNavigate } from 'react-router-dom'
import { useRef, useState, useEffect, useCallback } from 'react'
import type { GraphNode, GraphEdge } from './useGraphLayout'

const ACCENT: Record<GraphNode['type'], string> = {
  forest: '#22C55E',
  domain: '#4ADE80',
  server: '#818CF8',
  user:   '#FBBF24',
}

const FILL_OPACITY: Record<GraphNode['type'], number> = {
  forest: 0.10,
  domain: 0.08,
  server: 0.07,
  user:   0.07,
}

const TYPE_LABEL: Record<GraphNode['type'], string> = {
  forest: 'FORÊT',
  domain: 'DOMAINE',
  server: 'SERVEUR',
  user:   'UTILISATEUR',
}

const TAB_TARGET: Record<GraphNode['type'], string> = {
  forest: 'forests',
  domain: 'domains',
  server: 'servers',
  user:   'users',
}

function hexToRgba(hex: string, a: number) {
  const n = parseInt(hex.slice(1), 16)
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`
}

function bezierPath(from: GraphNode, to: GraphNode) {
  const x1 = from.x + from.width
  const y1 = from.y + from.height / 2
  const x2 = to.x
  const y2 = to.y + to.height / 2
  const cx = (x1 + x2) / 2
  return `M ${x1} ${y1} C ${cx} ${y1} ${cx} ${y2} ${x2} ${y2}`
}

interface Props { nodes: GraphNode[]; edges: GraphEdge[]; viewBox: string; projectId: number }

interface View { x: number; y: number; scale: number }

export function ADGraph({ nodes, edges, viewBox, projectId }: Props) {
  const navigate   = useNavigate()
  const containerRef = useRef<HTMLDivElement>(null)
  const [view, setView] = useState<View>({ x: 0, y: 0, scale: 1 })
  const dragging   = useRef(false)
  const hasDragged = useRef(false)
  const lastMouse  = useRef({ x: 0, y: 0 })

  const fitView = useCallback(() => {
    const el = containerRef.current
    if (!el || nodes.length === 0) return
    const [,, gW, gH] = viewBox.split(' ').map(Number)
    const cW = el.clientWidth
    const cH = el.clientHeight
    const s  = Math.min(cW / gW, cH / gH) * 0.88
    setView({ x: (cW - gW * s) / 2, y: (cH - gH * s) / 2, scale: s })
  }, [viewBox, nodes.length])

  useEffect(() => { fitView() }, [fitView])

  // Non-passive wheel listener to allow preventDefault
  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const onWheel = (e: WheelEvent) => {
      e.preventDefault()
      const factor = e.deltaY < 0 ? 1.12 : 1 / 1.12
      const rect = el.getBoundingClientRect()
      const cx = e.clientX - rect.left
      const cy = e.clientY - rect.top
      setView(v => {
        const ns = Math.max(0.15, Math.min(5, v.scale * factor))
        const r  = ns / v.scale
        return { x: cx - r * (cx - v.x), y: cy - r * (cy - v.y), scale: ns }
      })
    }
    el.addEventListener('wheel', onWheel, { passive: false })
    return () => el.removeEventListener('wheel', onWheel)
  }, [])

  const onMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return
    dragging.current  = true
    hasDragged.current = false
    lastMouse.current = { x: e.clientX, y: e.clientY }
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
    const cx = el.clientWidth / 2
    const cy = el.clientHeight / 2
    setView(v => {
      const ns = Math.max(0.15, Math.min(5, v.scale * factor))
      const r  = ns / v.scale
      return { x: cx - r * (cx - v.x), y: cy - r * (cy - v.y), scale: ns }
    })
  }

  const getNode = (id: string) => nodes.find(n => n.id === id)

  if (nodes.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', padding: '48px 24px', gap: 10 }}>
        <svg width={40} height={40} viewBox="0 0 24 24" fill="none" style={{ opacity: 0.2 }}>
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
            stroke="var(--text-muted)" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <p style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 11,
          color: 'var(--text-dim)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
          Créez des forêts, domaines et serveurs
        </p>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>

      {/* Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
        {/* Legend */}
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          {(Object.keys(ACCENT) as GraphNode['type'][]).map(type => (
            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <div style={{ width: 9, height: 9, borderRadius: 2, flexShrink: 0,
                background: hexToRgba(ACCENT[type], 0.2),
                border: `1.5px solid ${ACCENT[type]}` }} />
              <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 9,
                color: 'var(--text-dim)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                {TYPE_LABEL[type]}
              </span>
            </div>
          ))}
        </div>

        {/* Controls */}
        <div style={{ display: 'flex', gap: 4 }}>
          {[
            { label: '+', action: () => zoom(1.25) },
            { label: '−', action: () => zoom(1 / 1.25) },
            { label: '⊡', action: fitView },
          ].map(btn => (
            <button key={btn.label} onClick={btn.action} style={{
              width: 26, height: 26,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderRadius: 5,
              border: '1px solid var(--border-base)',
              background: 'var(--bg-input)',
              color: 'var(--text-muted)',
              fontSize: btn.label === '⊡' ? 14 : 16,
              cursor: 'pointer',
              fontFamily: 'monospace',
              lineHeight: 1,
            }}>
              {btn.label}
            </button>
          ))}
        </div>
      </div>

      {/* Graph viewport */}
      <div
        ref={containerRef}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
        style={{
          position: 'relative',
          height: 380,
          overflow: 'hidden',
          borderRadius: 8,
          border: '1px solid var(--border-base)',
          background: 'var(--bg-card)',
          cursor: dragging.current ? 'grabbing' : 'grab',
          userSelect: 'none',
        }}
      >
        <svg
          width="100%"
          height="100%"
          style={{ display: 'block' }}
        >
          <defs>
            {edges.map((edge, i) => {
              const from = getNode(edge.from)
              const to   = getNode(edge.to)
              if (!from || !to) return null
              return (
                <linearGradient key={i} id={`eg${i}`} x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%"   stopColor={ACCENT[from.type]} stopOpacity={0.45} />
                  <stop offset="100%" stopColor={ACCENT[to.type]}   stopOpacity={0.45} />
                </linearGradient>
              )
            })}
          </defs>

          <g transform={`translate(${view.x},${view.y}) scale(${view.scale})`}>
            {/* Edges */}
            {edges.map((edge, i) => {
              const from = getNode(edge.from)
              const to   = getNode(edge.to)
              if (!from || !to) return null
              return (
                <path key={i} d={bezierPath(from, to)} fill="none"
                  stroke={`url(#eg${i})`} strokeWidth={1.5} />
              )
            })}

            {/* Nodes */}
            {nodes.map(node => {
              const accent = ACCENT[node.type]
              const truncLabel = node.label.length > 20
                ? node.label.slice(0, 18) + '…'
                : node.label

              return (
                <g
                  key={node.id}
                  onClick={() => { if (!hasDragged.current) navigate(`/projects/${projectId}?tab=${TAB_TARGET[node.type]}`) }}
                  style={{ cursor: 'pointer' }}
                >
                  <rect x={node.x} y={node.y} width={node.width} height={node.height}
                    rx={6}
                    fill={hexToRgba(accent, FILL_OPACITY[node.type])}
                    stroke={accent} strokeWidth={1} strokeOpacity={0.35}
                  />
                  <rect x={node.x} y={node.y} width={3} height={node.height}
                    rx={2} fill={accent} opacity={0.8} />
                  <text x={node.x + 12} y={node.y + 18}
                    fill={accent} fontSize={8} fontWeight={700}
                    fontFamily="'IBM Plex Mono', monospace" letterSpacing={1.5} opacity={0.8}>
                    {TYPE_LABEL[node.type]}
                  </text>
                  <text x={node.x + 12} y={node.y + 38}
                    fill="var(--text-bright)" fontSize={11.5}
                    fontFamily="'Fira Code', monospace" fontWeight={500}>
                    <title>{node.label}</title>
                    {truncLabel}
                  </text>
                  {node.meta?.is_dc && (
                    <>
                      <rect x={node.x + node.width - 28} y={node.y + 6}
                        width={22} height={13} rx={3}
                        fill={hexToRgba('#10B981', 0.15)}
                        stroke="#10B981" strokeWidth={0.75} strokeOpacity={0.6} />
                      <text x={node.x + node.width - 17} y={node.y + 13}
                        textAnchor="middle" dominantBaseline="middle"
                        fill="#10B981" fontSize={7.5} fontWeight={700}
                        fontFamily="'IBM Plex Mono', monospace" letterSpacing={0.5}>
                        DC
                      </text>
                    </>
                  )}
                </g>
              )
            })}
          </g>
        </svg>

        {/* Scale indicator */}
        <div style={{
          position: 'absolute', bottom: 8, right: 10,
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 9, color: 'var(--text-dim)',
          letterSpacing: '0.08em',
        }}>
          {Math.round(view.scale * 100)}%
        </div>
      </div>
    </div>
  )
}

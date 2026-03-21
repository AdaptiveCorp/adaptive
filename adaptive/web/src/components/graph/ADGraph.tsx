import { useNavigate } from 'react-router-dom'
import type { GraphNode, GraphEdge } from './useGraphLayout'

const accent: Record<GraphNode['type'], string> = {
  forest: '#3B82F6',
  domain: '#0EA5E9',
  server: '#8B5CF6',
  user:   '#10B981',
}

const fill: Record<GraphNode['type'], string> = {
  forest: 'rgba(59,130,246,0.08)',
  domain: 'rgba(14,165,233,0.07)',
  server: 'rgba(139,92,246,0.07)',
  user:   'rgba(16,185,129,0.07)',
}

const tabTarget: Record<GraphNode['type'], string> = {
  forest: 'forests',
  domain: 'domains',
  server: 'servers',
  user:   'users',
}

interface Props { nodes: GraphNode[]; edges: GraphEdge[]; viewBox: string; projectId: number }

export function ADGraph({ nodes, edges, viewBox, projectId }: Props) {
  const navigate = useNavigate()

  if (nodes.length === 0) {
    return (
      <p className="text-center py-10 text-sm text-slate-600">
        Aucune donnée — créez des forêts, domaines et serveurs.
      </p>
    )
  }

  const getNode = (id: string) => nodes.find((n) => n.id === id)

  function bezierPath(from: GraphNode, to: GraphNode) {
    const x1 = from.x + from.width, y1 = from.y + from.height / 2
    const x2 = to.x,               y2 = to.y + to.height / 2
    const cx = (x1 + x2) / 2
    return `M ${x1} ${y1} C ${cx} ${y1}, ${cx} ${y2}, ${x2} ${y2}`
  }

  return (
    <svg viewBox={viewBox} width="100%" className="overflow-visible">
      {edges.map((edge, i) => {
        const from = getNode(edge.from), to = getNode(edge.to)
        if (!from || !to) return null
        return (
          <path key={i} d={bezierPath(from, to)} fill="none"
            stroke="rgba(255,255,255,0.07)" strokeWidth={1.5} />
        )
      })}

      {nodes.map((node) => {
        const a = accent[node.type], f = fill[node.type]
        const truncated = node.label.length > 18 ? node.label.slice(0, 16) + '…' : node.label

        return (
          <g key={node.id}
            onClick={() => navigate(`/projects/${projectId}?tab=${tabTarget[node.type]}`)}
            style={{ cursor: 'pointer' }}>
            <rect x={node.x} y={node.y} width={node.width} height={node.height}
              rx={4} fill={f} stroke={a} strokeWidth={1} strokeOpacity={0.5} />
            <text
              x={node.x + node.width / 2} y={node.y + node.height / 2 + 1}
              textAnchor="middle" dominantBaseline="middle"
              fill="rgba(226,232,240,0.85)" fontSize={9.5}
              fontFamily="'JetBrains Mono', monospace">
              <title>{node.label}</title>
              {truncated}
            </text>
            {node.meta?.is_dc && (
              <>
                <rect x={node.x + node.width - 24} y={node.y + 4} width={20} height={11}
                  rx={2} fill="rgba(16,185,129,0.12)" stroke="rgba(16,185,129,0.4)" strokeWidth={0.75} />
                <text x={node.x + node.width - 14} y={node.y + 9.5}
                  textAnchor="middle" dominantBaseline="middle"
                  fill="#10B981" fontSize={7} fontWeight="600" fontFamily="system-ui">
                  DC
                </text>
              </>
            )}
          </g>
        )
      })}
    </svg>
  )
}

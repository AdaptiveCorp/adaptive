import { TreePine, Network, Server, Users, ShieldAlert } from 'lucide-react'
import { ADGraph } from '../graph/ADGraph'
import { useGraphLayout } from '../graph/useGraphLayout'
import type { Forest, Domain, Server as SrvType, User } from '../../types'

interface Props {
  projectId: number
  forests: Forest[]
  domains: Domain[]
  servers: SrvType[]
  users: User[]
  vulnerabilitiesCount: number
}

const STATS = (forests: Forest[], domains: Domain[], servers: SrvType[], users: User[], vulns: number) => [
  { label: 'Forêts',        value: forests.length,  icon: TreePine,   color: 'var(--brand-300)' },
  { label: 'Domaines',      value: domains.length,  icon: Network,    color: 'var(--brand-400)' },
  { label: 'Serveurs',      value: servers.length,  icon: Server,     color: 'var(--brand-300)' },
  { label: 'Utilisateurs',  value: users.length,    icon: Users,      color: '#FBBF24' },
  { label: 'Vulnérabilités',value: vulns,           icon: ShieldAlert,color: '#FB7185' },
]

export function DashboardTab({ projectId, forests, domains, servers, users, vulnerabilitiesCount }: Props) {
  const { nodes, edges, viewBox } = useGraphLayout(forests, domains, servers, users)
  const stats = STATS(forests, domains, servers, users, vulnerabilitiesCount)

  return (
    <div className="space-y-5">
      {/* Stats grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap: 10,
      }}>
        {stats.map((s, i) => {
          const Icon = s.icon
          return (
            <div
              key={s.label}
              className="animate-enter"
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-card)',
                borderTop: `3px solid ${s.color}`,
                borderRadius: '0 0 10px 10px',
                padding: '14px 16px 16px',
                animationDelay: `${i * 50}ms`,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <span style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: 9,
                  fontWeight: 600,
                  color: 'var(--text-dim)',
                  letterSpacing: '0.12em',
                  textTransform: 'uppercase',
                }}>
                  {s.label}
                </span>
                <Icon style={{ width: 12, height: 12, color: s.color, opacity: 0.55, flexShrink: 0 }} />
              </div>
              <span style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 40,
                fontWeight: 600,
                color: s.color,
                lineHeight: 1,
                letterSpacing: '-0.04em',
                display: 'block',
              }}>
                {String(s.value).padStart(2, '0')}
              </span>
            </div>
          )
        })}
      </div>

      {/* Graph */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-card)',
        borderRadius: 10,
        padding: '20px',
      }}>
        <p style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 9,
          fontWeight: 600,
          color: 'var(--text-dim)',
          textTransform: 'uppercase',
          letterSpacing: '0.14em',
          marginBottom: 16,
        }}>
          Hiérarchie AD
        </p>
        <ADGraph nodes={nodes} edges={edges} viewBox={viewBox} projectId={projectId} />
      </div>
    </div>
  )
}

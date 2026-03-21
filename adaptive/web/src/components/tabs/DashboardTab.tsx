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
  {
    label: 'Forêts',
    value: forests.length,
    icon: TreePine,
    color: '#38BDF8',
    bg: 'rgba(14, 165, 233, 0.1)',
    glow: 'rgba(14, 165, 233, 0.18)',
    border: 'rgba(14, 165, 233, 0.2)',
  },
  {
    label: 'Domaines',
    value: domains.length,
    icon: Network,
    color: '#818CF8',
    bg: 'rgba(129, 140, 248, 0.1)',
    glow: 'rgba(129, 140, 248, 0.18)',
    border: 'rgba(129, 140, 248, 0.2)',
  },
  {
    label: 'Serveurs',
    value: servers.length,
    icon: Server,
    color: '#34D399',
    bg: 'rgba(52, 211, 153, 0.1)',
    glow: 'rgba(52, 211, 153, 0.18)',
    border: 'rgba(52, 211, 153, 0.2)',
  },
  {
    label: 'Utilisateurs',
    value: users.length,
    icon: Users,
    color: '#FBBF24',
    bg: 'rgba(251, 191, 36, 0.1)',
    glow: 'rgba(251, 191, 36, 0.18)',
    border: 'rgba(251, 191, 36, 0.2)',
  },
  {
    label: 'Vulnérabilités',
    value: vulns,
    icon: ShieldAlert,
    color: '#FB7185',
    bg: 'rgba(251, 113, 133, 0.1)',
    glow: 'rgba(251, 113, 133, 0.18)',
    border: 'rgba(251, 113, 133, 0.2)',
  },
]

export function DashboardTab({ projectId, forests, domains, servers, users, vulnerabilitiesCount }: Props) {
  const { nodes, edges, viewBox } = useGraphLayout(forests, domains, servers, users)
  const stats = STATS(forests, domains, servers, users, vulnerabilitiesCount)

  return (
    <div className="space-y-5">
      {/* Stats grid */}
      <div style={{ display: 'flex', gap: 12 }}>
        {stats.map((s, i) => {
          const Icon = s.icon
          return (
            <div
              key={s.label}
              className="animate-enter"
              style={{
                flex: 1,
                background: 'rgba(10, 23, 40, 0.9)',
                border: '1px solid rgba(22, 40, 64, 0.85)',
                borderRadius: 10,
                padding: '16px 18px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.4)',
                animationDelay: `${i * 50}ms`,
              }}
            >
              {/* Top: label + icon */}
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 14 }}>
                <span style={{
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: 10,
                  fontWeight: 600,
                  color: '#475569',
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                }}>
                  {s.label}
                </span>
                <div style={{
                  width: 30,
                  height: 30,
                  borderRadius: 7,
                  background: s.bg,
                  border: `1px solid ${s.border}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: s.color,
                  boxShadow: `0 0 10px ${s.glow}`,
                  flexShrink: 0,
                }}>
                  <Icon style={{ width: 14, height: 14 }} />
                </div>
              </div>

              {/* Value */}
              <span style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 34,
                fontWeight: 600,
                color: '#E2E8F0',
                lineHeight: 1,
                letterSpacing: '-0.03em',
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
        background: 'rgba(10, 23, 40, 0.9)',
        border: '1px solid rgba(22, 40, 64, 0.85)',
        borderRadius: 10,
        padding: '20px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.4)',
      }}>
        <p style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 10,
          fontWeight: 600,
          color: '#475569',
          textTransform: 'uppercase',
          letterSpacing: '0.12em',
          marginBottom: 16,
        }}>
          Hiérarchie AD
        </p>
        <ADGraph nodes={nodes} edges={edges} viewBox={viewBox} projectId={projectId} />
      </div>
    </div>
  )
}

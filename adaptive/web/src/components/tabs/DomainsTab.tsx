import { useState } from 'react'
import { Plus, Network } from 'lucide-react'
import { Badge } from '../Badge'
import { CreateDomainModal } from '../modals/CreateDomainModal'
import type { Forest, Domain, Server as SrvType } from '../../types'

interface Props { projectId: number; forests: Forest[]; domains: Domain[]; servers: SrvType[] }

export function DomainsTab({ projectId, forests, domains, servers }: Props) {
  const [open, setOpen] = useState(false)
  const srvCount = (id: number) => servers.filter((s) => s.domain_id === id).length
  const forestOf = (fid: number) => forests.find((f) => f.id === fid)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 10,
          fontWeight: 600,
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
        }}>
          Domaines AD
        </span>
        <button
          className="btn-ghost"
          style={{ padding: '5px 12px', fontSize: 12 }}
          onClick={() => setOpen(true)}
          disabled={forests.length === 0}
          title={forests.length === 0 ? "Créez d'abord une forêt" : undefined}
        >
          <Plus className="w-3.5 h-3.5" /> Ajouter
        </button>
      </div>

      <div className="tbl-wrap">
        <div className="tbl-head" style={{ gridTemplateColumns: '1fr 180px 80px' }}>
          <span>FQDN</span><span>Forêt parente</span><span className="text-center">Serveurs</span>
        </div>

        {domains.length === 0 ? (
          <div className="tbl-empty">
            {forests.length === 0
              ? 'Créez d\'abord une forêt.'
              : (
                <span>
                  Aucun domaine —{' '}
                  <button
                    style={{ color: 'var(--brand-300)', background: 'none', border: 'none', cursor: 'pointer', fontFamily: "'Fira Code', monospace", fontSize: 13 }}
                    onClick={() => setOpen(true)}
                  >
                    en ajouter un
                  </button>
                </span>
              )
            }
          </div>
        ) : domains.map((d) => {
          const forest = forestOf(d.forest_id)
          return (
            <div key={d.id} className="tbl-row" style={{ gridTemplateColumns: '1fr 180px 80px' }}>
              <div className="flex items-center gap-2.5 min-w-0">
                <Network style={{ width: 13, height: 13, color: 'var(--brand-400)', flexShrink: 0 }} />
                <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 13, color: 'var(--text-bright)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {d.fqdn}
                </span>
              </div>
              <div className="min-w-0 self-center">
                {forest && <Badge label={forest.fqdn} variant="blue" />}
              </div>
              <span style={{
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 13,
                color: 'var(--text-dim)',
                textAlign: 'center',
                display: 'block',
              }}>
                {srvCount(d.id)}
              </span>
            </div>
          )
        })}
      </div>

      {open && (
        <CreateDomainModal projectId={projectId} forests={forests} onSuccess={() => setOpen(false)} onClose={() => setOpen(false)} />
      )}
    </div>
  )
}

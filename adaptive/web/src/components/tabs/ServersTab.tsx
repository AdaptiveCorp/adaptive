import { useState } from 'react'
import { Plus, Server } from 'lucide-react'
import { Badge } from '../Badge'
import { CreateServerModal } from '../modals/CreateServerModal'
import type { Domain, Server as SrvType } from '../../types'

interface Props { projectId: number; domains: Domain[]; servers: SrvType[] }

export function ServersTab({ projectId, domains, servers }: Props) {
  const [open, setOpen] = useState(false)
  const domainOf = (did: number | null) => did ? domains.find((d) => d.id === did) : undefined

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 10,
          fontWeight: 600,
          color: '#475569',
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
        }}>
          Serveurs AD
        </span>
        <button
          className="btn-ghost"
          style={{ padding: '5px 12px', fontSize: 12 }}
          onClick={() => setOpen(true)}
          disabled={domains.length === 0}
          title={domains.length === 0 ? "Créez d'abord un domaine" : undefined}
        >
          <Plus className="w-3.5 h-3.5" /> Ajouter
        </button>
      </div>

      <div className="tbl-wrap">
        <div className="tbl-head" style={{ gridTemplateColumns: '1fr 110px 170px 80px' }}>
          <span>FQDN</span><span>IP</span><span>Domaine</span><span>Rôle</span>
        </div>

        {servers.length === 0 ? (
          <div className="tbl-empty">
            {domains.length === 0
              ? 'Créez d\'abord un domaine.'
              : (
                <span>
                  Aucun serveur —{' '}
                  <button
                    style={{ color: '#38BDF8', background: 'none', border: 'none', cursor: 'pointer', fontFamily: "'Fira Code', monospace", fontSize: 13 }}
                    onClick={() => setOpen(true)}
                  >
                    en ajouter un
                  </button>
                </span>
              )
            }
          </div>
        ) : servers.map((s) => {
          const dom = domainOf(s.domain_id)
          return (
            <div key={s.id} className="tbl-row" style={{ gridTemplateColumns: '1fr 110px 170px 80px' }}>
              <div className="flex items-center gap-2.5 min-w-0">
                <Server style={{ width: 13, height: 13, color: '#34D399', flexShrink: 0 }} />
                <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 13, color: '#CBD5E1', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {s.fqdn}
                </span>
              </div>
              <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 12, color: '#64748B', alignSelf: 'center' }}>
                {s.ip ?? '—'}
              </span>
              <div className="self-center min-w-0">
                {dom && <Badge label={dom.fqdn} variant="blue" />}
              </div>
              <div className="self-center">
                <Badge label={s.is_dc ? 'DC' : 'Membre'} variant={s.is_dc ? 'green' : 'gray'} />
              </div>
            </div>
          )
        })}
      </div>

      {open && (
        <CreateServerModal projectId={projectId} domains={domains} onSuccess={() => setOpen(false)} onClose={() => setOpen(false)} />
      )}
    </div>
  )
}

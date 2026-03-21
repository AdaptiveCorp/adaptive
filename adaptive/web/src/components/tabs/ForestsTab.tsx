import { useState } from 'react'
import { Plus, TreePine } from 'lucide-react'
import { CreateForestModal } from '../modals/CreateForestModal'
import type { Forest, Domain } from '../../types'

interface Props { projectId: number; forests: Forest[]; domains: Domain[] }

export function ForestsTab({ projectId, forests, domains }: Props) {
  const [open, setOpen] = useState(false)
  const domCount = (id: number) => domains.filter((d) => d.forest_id === id).length

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
          Forêts AD
        </span>
        <button className="btn-ghost" style={{ padding: '5px 12px', fontSize: 12 }} onClick={() => setOpen(true)}>
          <Plus className="w-3.5 h-3.5" /> Ajouter
        </button>
      </div>

      <div className="tbl-wrap">
        <div className="tbl-head" style={{ gridTemplateColumns: '1fr 100px' }}>
          <span>FQDN</span><span className="text-center">Domaines</span>
        </div>

        {forests.length === 0 ? (
          <div className="tbl-empty">
            Aucune forêt —{' '}
            <button
              style={{ color: '#38BDF8', background: 'none', border: 'none', cursor: 'pointer', fontFamily: "'Fira Code', monospace", fontSize: 13 }}
              onClick={() => setOpen(true)}
            >
              en ajouter une
            </button>
          </div>
        ) : forests.map((f) => (
          <div key={f.id} className="tbl-row" style={{ gridTemplateColumns: '1fr 100px' }}>
            <div className="flex items-center gap-2.5">
              <TreePine style={{ width: 13, height: 13, color: '#38BDF8', flexShrink: 0 }} />
              <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 13, color: '#CBD5E1' }}>
                {f.fqdn}
              </span>
            </div>
            <span style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: 13,
              color: '#64748B',
              textAlign: 'center',
              display: 'block',
            }}>
              {domCount(f.id)}
            </span>
          </div>
        ))}
      </div>

      {open && (
        <CreateForestModal projectId={projectId} onSuccess={() => setOpen(false)} onClose={() => setOpen(false)} />
      )}
    </div>
  )
}

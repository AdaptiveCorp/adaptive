import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ShieldAlert, Trash2, Tag } from 'lucide-react'
import { vulnerabilitiesApi } from '../../api/vulnerabilities'
import { Badge } from '../Badge'
import { Spinner } from '../Spinner'
import { Modal } from '../Modal'
import type { AppliedVulnerability } from '../../types'

interface Props {
  projectId: number
}

const categoryColors: Record<string, 'red' | 'yellow' | 'blue' | 'green' | 'gray'> = {
  kerberos: 'red',
  privilege: 'yellow',
  credential: 'red',
  lateral: 'yellow',
  recon: 'blue',
  misc: 'gray',
}

function categoryVariant(cat: string | null) {
  if (!cat) return 'gray' as const
  const key = Object.keys(categoryColors).find((k) => cat.toLowerCase().includes(k))
  return key ? categoryColors[key] : 'gray' as const
}

export function VulnerabilitiesSection({ projectId }: Props) {
  const queryClient = useQueryClient()
  const [removeTarget, setRemoveTarget] = useState<AppliedVulnerability | null>(null)

  const { data: applied, isLoading } = useQuery({
    queryKey: ['applied-vulns', projectId],
    queryFn: () => vulnerabilitiesApi.listApplied(projectId),
  })

  const { data: catalog } = useQuery({
    queryKey: ['vulnerabilities'],
    queryFn: () => vulnerabilitiesApi.list(),
  })

  const removeMutation = useMutation({
    mutationFn: (id: number) => vulnerabilitiesApi.removeApplied(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applied-vulns', projectId] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      setRemoveTarget(null)
    },
  })

  return (
    <div className="space-y-5">
      {/* Applied vulnerabilities */}
      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <span style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: 10,
            fontWeight: 600,
            color: '#475569',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
          }}>
            Vulnérabilités appliquées
          </span>
          <span style={{
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: 11,
            color: '#475569',
          }}>
            {applied?.length ?? 0} / {catalog?.length ?? '…'}
          </span>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-6">
            <Spinner className="w-5 h-5 text-brand-400" />
          </div>
        ) : !applied?.length ? (
          <p style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: '#475569', textAlign: 'center', padding: '20px 0' }}>
            Aucune vulnérabilité appliquée à ce projet.
          </p>
        ) : (
          <div className="space-y-2">
            {applied.map((av) => (
              <div
                key={av.id}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 12,
                  background: 'rgba(15, 32, 52, 0.6)',
                  border: '1px solid rgba(22, 40, 64, 0.7)',
                  borderRadius: 8,
                  padding: '12px 14px',
                  transition: 'border-color 0.15s',
                }}
                className="group"
              >
                <ShieldAlert style={{ width: 15, height: 15, color: '#FB7185', marginTop: 2, flexShrink: 0 }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
                    <span style={{ fontSize: 13, fontWeight: 600, color: '#CBD5E1' }}>
                      {av.template.name}
                    </span>
                    <span style={{
                      fontFamily: "'Fira Code', monospace",
                      fontSize: 11,
                      color: '#64748B',
                      background: 'rgba(6, 16, 28, 0.8)',
                      border: '1px solid rgba(22, 40, 64, 0.7)',
                      borderRadius: 4,
                      padding: '1px 6px',
                    }}>
                      {av.template.code}
                    </span>
                    {av.domain_id && <Badge label={`Domain #${av.domain_id}`} variant="blue" />}
                    {av.user_id && <Badge label={`User #${av.user_id}`} variant="yellow" />}
                    {av.server_id && <Badge label={`Server #${av.server_id}`} variant="gray" />}
                    {av.forest_id && <Badge label={`Forest #${av.forest_id}`} variant="green" />}
                  </div>
                  {av.params && (
                    <pre style={{ fontFamily: "'Fira Code', monospace", fontSize: 11, color: '#64748B', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {av.params}
                    </pre>
                  )}
                  <p style={{ fontSize: 11, color: '#475569', marginTop: 3, fontFamily: "'IBM Plex Mono', monospace" }}>
                    {new Date(av.created_at).toLocaleDateString('fr-FR')}
                  </p>
                </div>
                <button
                  onClick={() => setRemoveTarget(av)}
                  style={{
                    background: 'none', border: 'none', cursor: 'pointer',
                    color: '#475569', transition: 'all 0.15s', padding: 4, borderRadius: 4,
                    opacity: 0,
                  }}
                  className="group-hover:opacity-100"
                  onMouseEnter={e => { e.currentTarget.style.color = '#FB7185'; e.currentTarget.style.background = 'rgba(244, 63, 94, 0.1)'; e.currentTarget.style.opacity = '1' }}
                  onMouseLeave={e => { e.currentTarget.style.color = '#475569'; e.currentTarget.style.background = 'none' }}
                >
                  <Trash2 style={{ width: 14, height: 14 }} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Catalog */}
      {catalog && catalog.length > 0 && (
        <div className="card space-y-3">
          <div className="flex items-center gap-2">
            <Tag style={{ width: 13, height: 13, color: '#475569' }} />
            <span style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: 10,
              fontWeight: 600,
              color: '#475569',
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
            }}>
              Catalogue disponible
            </span>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {catalog.map((v) => (
              <div
                key={v.id}
                title={v.description ?? ''}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  background: 'rgba(15, 32, 52, 0.6)',
                  border: '1px solid rgba(22, 40, 64, 0.7)',
                  borderRadius: 6,
                  padding: '6px 10px',
                  cursor: 'default',
                }}
              >
                <Badge label={v.category ?? 'misc'} variant={categoryVariant(v.category)} />
                <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 12, color: '#94A3B8' }}>
                  {v.code}
                </span>
                <span style={{ fontSize: 12, color: '#64748B' }}>— {v.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Remove confirm */}
      {removeTarget && (
        <Modal title="Supprimer la vulnérabilité" onClose={() => setRemoveTarget(null)}>
          <p style={{ fontSize: 13, color: '#94A3B8', marginBottom: 20, lineHeight: 1.6 }}>
            Supprimer{' '}
            <span style={{ fontFamily: "'Fira Code', monospace", color: '#E2E8F0', fontWeight: 500 }}>
              {removeTarget.template.name}
            </span>{' '}
            de ce projet ?
          </p>
          <div className="flex gap-2 justify-end">
            <button className="btn-ghost" onClick={() => setRemoveTarget(null)}>Annuler</button>
            <button
              className="btn-danger"
              disabled={removeMutation.isPending}
              onClick={() => removeMutation.mutate(removeTarget.id)}
            >
              {removeMutation.isPending && <Spinner className="w-4 h-4" />}
              Supprimer
            </button>
          </div>
        </Modal>
      )}
    </div>
  )
}

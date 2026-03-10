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
  if (!cat) return 'gray'
  const key = Object.keys(categoryColors).find((k) => cat.toLowerCase().includes(k))
  return key ? categoryColors[key] : 'gray'
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
    <div className="card space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Vulnérabilités appliquées
        </h2>
        <span className="text-xs text-slate-500">
          {applied?.length ?? 0} / {catalog?.length ?? '…'} disponibles
        </span>
      </div>

      {/* List */}
      {isLoading ? (
        <div className="flex justify-center py-6">
          <Spinner className="w-5 h-5 text-brand-400" />
        </div>
      ) : !applied?.length ? (
        <p className="text-slate-500 text-sm text-center py-4">
          Aucune vulnérabilité appliquée à ce projet.
        </p>
      ) : (
        <div className="space-y-2">
          {applied.map((av) => (
            <div
              key={av.id}
              className="flex items-start gap-3 bg-dark-700 rounded-xl px-4 py-3 group"
            >
              <ShieldAlert className="w-4 h-4 text-danger-400 mt-0.5 shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-medium text-slate-200">
                    {av.vulnerability.name}
                  </span>
                  <span className="text-xs font-mono text-slate-500 bg-dark-800 px-1.5 py-0.5 rounded">
                    {av.vulnerability.code}
                  </span>
                  {av.domain_id && <Badge label={`Domain #${av.domain_id}`} variant="blue" />}
                  {av.user_id && <Badge label={`User #${av.user_id}`} variant="yellow" />}
                  {av.server_id && <Badge label={`Server #${av.server_id}`} variant="gray" />}
                  {av.forest_id && <Badge label={`Forest #${av.forest_id}`} variant="green" />}
                </div>
                {av.params && (
                  <pre className="text-xs text-slate-500 mt-1 font-mono truncate">{av.params}</pre>
                )}
                <p className="text-xs text-slate-600 mt-0.5">
                  {new Date(av.created_at).toLocaleDateString('fr-FR')}
                </p>
              </div>
              <button
                onClick={() => setRemoveTarget(av)}
                className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-danger-400 transition"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Catalog preview */}
      {catalog && catalog.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase mb-2 flex items-center gap-1.5">
            <Tag className="w-3.5 h-3.5" /> Catalogue disponible
          </h3>
          <div className="flex flex-wrap gap-2">
            {catalog.map((v) => (
              <div
                key={v.id}
                className="flex items-center gap-1.5 bg-dark-700 rounded-lg px-2.5 py-1.5"
                title={v.description ?? ''}
              >
                <Badge label={v.category ?? 'misc'} variant={categoryVariant(v.category)} />
                <span className="text-xs text-slate-300 font-mono">{v.code}</span>
                <span className="text-xs text-slate-500">– {v.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Remove confirm */}
      {removeTarget && (
        <Modal title="Supprimer la vulnérabilité" onClose={() => setRemoveTarget(null)}>
          <p className="text-slate-300 text-sm">
            Supprimer{' '}
            <span className="font-semibold text-slate-100">
              {removeTarget.vulnerability.name}
            </span>{' '}
            de ce projet ?
          </p>
          <div className="flex gap-2 justify-end mt-5">
            <button className="btn-ghost" onClick={() => setRemoveTarget(null)}>
              Annuler
            </button>
            <button
              className="btn-danger flex items-center gap-2"
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

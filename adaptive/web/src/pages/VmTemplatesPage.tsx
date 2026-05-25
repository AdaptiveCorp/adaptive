import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Play, Trash2, HardDrive } from 'lucide-react'
import { vmTemplatesApi } from '../api/vm-templates'
import { Modal } from '../components/Modal'
import { Spinner } from '../components/Spinner'
import type { VmTemplate } from '../types'

export function VmTemplatesPage() {
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [delTarget, setDelTarget] = useState<VmTemplate | null>(null)
  const [deployingId, setDeployingId]   = useState<number | null>(null)
  const [deployErrorId, setDeployErrorId] = useState<number | null>(null)
  const [form, setForm] = useState({ name: '', vm_id: '', description: '' })

  const { data: templates, isLoading } = useQuery({
    queryKey: ['vm-templates'],
    queryFn: () => vmTemplatesApi.list(),
  })

  const createMut = useMutation({
    mutationFn: () =>
      vmTemplatesApi.create({
        name: form.name.trim(),
        vm_id: Number(form.vm_id),
        description: form.description.trim() || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vm-templates'] })
      setShowCreate(false)
      setForm({ name: '', vm_id: '', description: '' })
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => vmTemplatesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vm-templates'] })
      setDelTarget(null)
    },
  })

  const deployMut = useMutation({
    mutationFn: (id: number) => vmTemplatesApi.deploy(id),
    onMutate:  (id) => { setDeployingId(id); setDeployErrorId(null) },
    onError:   (_, id) => setDeployErrorId(id),
    onSettled: () => setDeployingId(null),
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <p className="page-eyebrow">// proxmox · packer-images</p>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="page-title">Templates VM</h1>
            <p className="page-subtitle">
              Images Packer Proxmox utilisées pour cloner les serveurs
            </p>
          </div>
          {/* <button className="btn-primary" style={{ marginTop: 4 }} onClick={() => setShowCreate(true)}>
            <Plus className="w-3.5 h-3.5" /> Nouveau template
          </button> */}
        </div>
      </div>

      <div style={{ height: 1, background: 'var(--border-base)' }} />

      {/* List */}
      {isLoading ? (
        <div className="flex justify-center py-20">
          <Spinner className="w-5 h-5 text-brand-400" />
        </div>
      ) : !templates?.length ? (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px dashed var(--border-input)',
          borderRadius: 12,
          padding: '64px 24px',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 16,
        }}>
          <div style={{
            width: 52,
            height: 52,
            borderRadius: 12,
            background: 'rgba(var(--brand-500-rgb), 0.08)',
            border: '1px solid rgba(var(--brand-500-rgb), 0.14)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <HardDrive style={{ width: 22, height: 22, color: 'var(--brand-400)', opacity: 0.5 }} />
          </div>
          <div>
            <p style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: 12,
              fontWeight: 600,
              color: 'var(--text-dim)',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: 6,
            }}>
              Aucun template VM
            </p>
            <p style={{ fontSize: 13, color: 'var(--text-dim)' }}>
              Ajoutez un template Packer pour pouvoir cloner des serveurs.
            </p>
          </div>
          {/* <button className="btn-primary" onClick={() => setShowCreate(true)} style={{ marginTop: 4 }}>
            <Plus className="w-3.5 h-3.5" /> Ajouter un template
          </button> */}
        </div>
      ) : (
        <div className="space-y-2">
          {templates.map((t, i) => (
            <div
              key={t.id}
              className="animate-enter"
              style={{ animationDelay: `${i * 40}ms` }}
            >
              <TemplateRow
              template={t}
              onDelete={() => setDelTarget(t)}
              onDeploy={() => deployMut.mutate(t.id)}
              isDeploying={deployingId === t.id}
              deployError={deployErrorId === t.id}
            />
            </div>
          ))}
        </div>
      )}

      {/* Create modal */}
      {showCreate && (
        <Modal title="Nouveau template VM" onClose={() => setShowCreate(false)}>
          <form
            onSubmit={(e) => {
              e.preventDefault()
              if (form.name.trim() && form.vm_id) createMut.mutate()
            }}
            className="space-y-4"
          >
            <div>
              <label>Nom</label>
              <input
                className="input"
                placeholder="ex: win-srv-2022"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                autoFocus
              />
            </div>
            <div>
              <label>VM ID Proxmox</label>
              <input
                className="input"
                type="number"
                placeholder="ex: 9000"
                value={form.vm_id}
                onChange={(e) => setForm({ ...form, vm_id: e.target.value })}
              />
            </div>
            <div>
              <label>
                Description{' '}
                <span style={{ color: 'var(--text-dim)', textTransform: 'none', fontSize: 10 }}>
                  (optionnel)
                </span>
              </label>
              <input
                className="input"
                placeholder="ex: Windows Server 2022 Standard"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <div className="flex gap-2 justify-end">
              <button type="button" className="btn-ghost" onClick={() => setShowCreate(false)}>
                Annuler
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={!form.name.trim() || !form.vm_id || createMut.isPending}
              >
                {createMut.isPending && <Spinner className="w-3.5 h-3.5" />}
                Créer
              </button>
            </div>
            {createMut.isError && (
              <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace" }}>
                Erreur lors de la création (nom déjà utilisé ?).
              </p>
            )}
          </form>
        </Modal>
      )}

      {/* Delete confirm */}
      {delTarget && (
        <Modal title="Supprimer le template" onClose={() => setDelTarget(null)}>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20, lineHeight: 1.6 }}>
            Supprimer{' '}
            <span style={{ fontFamily: "'Fira Code', monospace", color: 'var(--text-bright)', fontWeight: 500 }}>
              {delTarget.name}
            </span>{' '}
            ? Impossible si des serveurs l'utilisent.
          </p>
          <div className="flex gap-2 justify-end">
            <button className="btn-ghost" onClick={() => setDelTarget(null)}>Annuler</button>
            <button
              className="btn-danger"
              disabled={deleteMut.isPending}
              onClick={() => deleteMut.mutate(delTarget.id)}
            >
              {deleteMut.isPending && <Spinner className="w-3.5 h-3.5" />}
              Supprimer
            </button>
          </div>
          {deleteMut.isError && (
            <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace", marginTop: 12 }}>
              Impossible de supprimer — des serveurs utilisent ce template.
            </p>
          )}
        </Modal>
      )}
    </div>
  )
}

function TemplateRow({
  template, onDelete, onDeploy, isDeploying, deployError,
}: {
  template: VmTemplate
  onDelete: () => void
  onDeploy: () => void
  isDeploying: boolean
  deployError: boolean
}) {
  return (
    <div className="project-row">
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontWeight: 600, fontSize: 15,
          color: 'var(--text-bright)', letterSpacing: '-0.02em',
          marginBottom: 3, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>
          {template.name}
        </p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 11, color: 'var(--text-muted)' }}>
            VM #{template.vm_id}
          </span>
          {template.description && (
            <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>
              — {template.description}
            </span>
          )}
          {deployError && (
            <span style={{ fontSize: 11, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace" }}>
              Erreur de déploiement
            </span>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <button
          onClick={(e) => { e.stopPropagation(); onDeploy() }}
          disabled={isDeploying}
          title="Déployer ce template"
          className="btn-ghost"
          style={{ padding: '5px 10px', fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}
        >
          {isDeploying
            ? <Spinner className="w-3.5 h-3.5" />
            : <Play style={{ width: 13, height: 13 }} />}
          Deploy
        </button>

        <button
          onClick={(e) => { e.stopPropagation(); onDelete() }}
          title="Supprimer"
          className="row-del"
        >
          <Trash2 style={{ width: 13, height: 13 }} />
        </button>
      </div>
    </div>
  )
}

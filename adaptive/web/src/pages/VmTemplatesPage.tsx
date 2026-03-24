import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, HardDrive, Box } from 'lucide-react'
import { vmTemplatesApi } from '../api/vm-templates'
import { Modal } from '../components/Modal'
import { Spinner } from '../components/Spinner'
import type { VmTemplate } from '../types'

export function VmTemplatesPage() {
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [delTarget, setDelTarget] = useState<VmTemplate | null>(null)
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <HardDrive className="w-4 h-4 text-brand-500" />
            <h1 style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontWeight: 600,
              fontSize: 18,
              color: '#E2E8F0',
              letterSpacing: '-0.02em',
            }}>
              Templates VM
            </h1>
          </div>
          <p style={{ fontSize: 13, color: '#64748B', letterSpacing: '0.01em' }}>
            Images Packer Proxmox utilisées pour cloner les serveurs
          </p>
        </div>
        <button className="btn-primary" onClick={() => setShowCreate(true)}>
          <Plus className="w-3.5 h-3.5" /> Nouveau template
        </button>
      </div>

      <div style={{ height: 1, background: 'rgba(22, 40, 64, 0.7)' }} />

      {/* List */}
      {isLoading ? (
        <div className="flex justify-center py-20">
          <Spinner className="w-5 h-5 text-brand-400" />
        </div>
      ) : !templates?.length ? (
        <div style={{
          background: 'rgba(10, 23, 40, 0.6)',
          border: '1px dashed rgba(22, 40, 64, 0.9)',
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
            background: 'rgba(14, 165, 233, 0.08)',
            border: '1px solid rgba(14, 165, 233, 0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Box className="w-6 h-6 text-dark-500" />
          </div>
          <div>
            <p style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontSize: 13,
              fontWeight: 600,
              color: '#475569',
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              marginBottom: 6,
            }}>
              Aucun template VM
            </p>
            <p style={{ fontSize: 13, color: '#475569' }}>
              Ajoutez un template Packer pour pouvoir cloner des serveurs.
            </p>
          </div>
          <button className="btn-primary" onClick={() => setShowCreate(true)} style={{ marginTop: 4 }}>
            <Plus className="w-3.5 h-3.5" /> Ajouter un template
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          {templates.map((t, i) => (
            <div
              key={t.id}
              className="animate-enter"
              style={{ animationDelay: `${i * 40}ms` }}
            >
              <TemplateRow template={t} onDelete={() => setDelTarget(t)} />
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
              <label>Description <span style={{ color: '#475569', textTransform: 'none', fontSize: 10 }}>(optionnel)</span></label>
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
          <p style={{ fontSize: 13, color: '#94A3B8', marginBottom: 20, lineHeight: 1.6 }}>
            Supprimer{' '}
            <span style={{ fontFamily: "'Fira Code', monospace", color: '#E2E8F0', fontWeight: 500 }}>
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

function TemplateRow({ template, onDelete }: { template: VmTemplate; onDelete: () => void }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: 14,
      background: 'rgba(10, 23, 40, 0.85)',
      border: '1px solid rgba(22, 40, 64, 0.85)',
      borderLeft: '3px solid rgba(14, 165, 233, 0.6)',
      borderRadius: '0 10px 10px 0',
      padding: '14px 18px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
      transition: 'all 0.2s ease',
    }}
      onMouseEnter={e => {
        const el = e.currentTarget
        el.style.borderLeftColor = '#38BDF8'
        el.style.background = 'rgba(15, 32, 52, 0.9)'
      }}
      onMouseLeave={e => {
        const el = e.currentTarget
        el.style.borderLeftColor = 'rgba(14, 165, 233, 0.6)'
        el.style.background = 'rgba(10, 23, 40, 0.85)'
      }}
    >
      <div style={{
        width: 36,
        height: 36,
        borderRadius: 8,
        background: 'rgba(14, 165, 233, 0.1)',
        border: '1px solid rgba(14, 165, 233, 0.18)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}>
        <HardDrive style={{ width: 16, height: 16, color: '#38BDF8' }} />
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontWeight: 600,
          fontSize: 14,
          color: '#E2E8F0',
          letterSpacing: '-0.01em',
          marginBottom: 2,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}>
          {template.name}
        </p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 11, color: '#64748B' }}>
            VM #{template.vm_id}
          </span>
          {template.description && (
            <span style={{ fontSize: 11, color: '#475569' }}>
              — {template.description}
            </span>
          )}
        </div>
      </div>

      <button
        onClick={(e) => { e.stopPropagation(); onDelete() }}
        title="Supprimer"
        style={{
          width: 30,
          height: 30,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: 6,
          border: 'none',
          background: 'transparent',
          color: '#475569',
          cursor: 'pointer',
          transition: 'all 0.15s',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.color = '#FB7185'
          e.currentTarget.style.background = 'rgba(244, 63, 94, 0.1)'
        }}
        onMouseLeave={e => {
          e.currentTarget.style.color = '#475569'
          e.currentTarget.style.background = 'transparent'
        }}
      >
        <Trash2 style={{ width: 13, height: 13 }} />
      </button>
    </div>
  )
}

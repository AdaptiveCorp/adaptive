import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Plus, Trash2, ArrowRight, FolderOpen } from 'lucide-react'
import { projectsApi } from '../api/projects'
import { Modal } from '../components/Modal'
import { Spinner } from '../components/Spinner'
import type { Project } from '../types'

export function ProjectsPage() {
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName]       = useState('')
  const [delTarget, setDelTarget]   = useState<Project | null>(null)

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list(),
  })

  const createMut = useMutation({
    mutationFn: (name: string) => projectsApi.create(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setShowCreate(false)
      setNewName('')
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => projectsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setDelTarget(null)
    },
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <p className="page-eyebrow">// red.team · lab-factory</p>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="page-title">Projets</h1>
            <p className="page-subtitle">
              Labs Active Directory — infrastructure de formation offensive
            </p>
          </div>
          <button className="btn-primary" style={{ marginTop: 4 }} onClick={() => setShowCreate(true)}>
            <Plus className="w-3.5 h-3.5" /> Nouveau projet
          </button>
        </div>
      </div>

      <div style={{ height: 1, background: 'var(--border-base)' }} />

      {/* Project list */}
      {isLoading ? (
        <div className="flex justify-center py-20">
          <Spinner className="w-5 h-5 text-brand-400" />
        </div>
      ) : !projects?.length ? (
        <EmptyState onCreateClick={() => setShowCreate(true)} />
      ) : (
        <div className="space-y-2">
          {projects.map((p, i) => (
            <div
              key={p.id}
              className="animate-enter"
              style={{ animationDelay: `${i * 40}ms` }}
            >
              <ProjectRow project={p} onDelete={() => setDelTarget(p)} />
            </div>
          ))}
        </div>
      )}

      {/* Create modal */}
      {showCreate && (
        <Modal title="Nouveau projet" onClose={() => setShowCreate(false)}>
          <form
            onSubmit={(e) => { e.preventDefault(); if (newName.trim()) createMut.mutate(newName.trim()) }}
            className="space-y-4"
          >
            <div>
              <label>Nom du projet</label>
              <input
                className="input"
                placeholder="lab-ctf-2026"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                autoFocus
              />
            </div>
            <div className="flex gap-2 justify-end">
              <button type="button" className="btn-ghost" onClick={() => setShowCreate(false)}>
                Annuler
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={!newName.trim() || createMut.isPending}
              >
                {createMut.isPending && <Spinner className="w-3.5 h-3.5" />}
                Créer
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Delete modal */}
      {delTarget && (
        <Modal title="Supprimer le projet" onClose={() => setDelTarget(null)}>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20, lineHeight: 1.6 }}>
            Supprimer{' '}
            <span style={{ fontFamily: "'Fira Code', monospace", color: 'var(--text-bright)', fontWeight: 500 }}>
              {delTarget.name}
            </span>{' '}
            ? Cette action est irréversible.
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
        </Modal>
      )}
    </div>
  )
}

function EmptyState({ onCreateClick }: { onCreateClick: () => void }) {
  return (
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
        <FolderOpen style={{ width: 24, height: 24, color: 'var(--brand-400)', opacity: 0.5 }} />
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
          Aucun projet défini
        </p>
        <p style={{ fontSize: 13, color: 'var(--text-dim)' }}>
          Créez votre premier lab Active Directory pour commencer.
        </p>
      </div>
      <button className="btn-primary" onClick={onCreateClick} style={{ marginTop: 4 }}>
        <Plus className="w-3.5 h-3.5" /> Créer un projet
      </button>
    </div>
  )
}

function ProjectRow({ project, onDelete }: { project: Project; onDelete: () => void }) {
  const date = new Date(project.created_at).toLocaleDateString('fr-FR', {
    day: '2-digit', month: 'short', year: 'numeric',
  })

  return (
    <div className="project-row">
      {/* Name + meta */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontWeight: 600,
          fontSize: 15,
          color: 'var(--text-bright)',
          letterSpacing: '-0.02em',
          marginBottom: 3,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}>
          {project.name}
        </p>
        <p style={{
          fontSize: 11,
          color: 'var(--text-dim)',
          fontFamily: "'IBM Plex Mono', monospace",
          letterSpacing: '0.02em',
        }}>
          <span style={{ color: 'var(--text-muted)' }}>
            #{String(project.id).padStart(3, '0')}
          </span>
          {' · '}
          {date}
        </p>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <button
          onClick={(e) => { e.stopPropagation(); onDelete() }}
          title="Supprimer"
          className="row-del"
        >
          <Trash2 style={{ width: 13, height: 13 }} />
        </button>
        <Link to={`/projects/${project.id}`} className="row-nav">
          <ArrowRight style={{ width: 13, height: 13 }} />
        </Link>
      </div>
    </div>
  )
}

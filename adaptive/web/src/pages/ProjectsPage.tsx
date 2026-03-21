import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Plus, Trash2, ArrowRight, FolderOpen, Terminal } from 'lucide-react'
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
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <Terminal className="w-4 h-4 text-brand-500" />
            <h1 style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontWeight: 600,
              fontSize: 18,
              color: '#E2E8F0',
              letterSpacing: '-0.02em',
            }}>
              Projets
            </h1>
          </div>
          <p style={{ fontSize: 13, color: '#64748B', letterSpacing: '0.01em' }}>
            Labs Active Directory — infrastructure de formation offensive
          </p>
        </div>
        <button className="btn-primary" onClick={() => setShowCreate(true)}>
          <Plus className="w-3.5 h-3.5" /> Nouveau projet
        </button>
      </div>

      {/* Divider */}
      <div style={{ height: 1, background: 'rgba(22, 40, 64, 0.7)' }} />

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
          <p style={{ fontSize: 13, color: '#94A3B8', marginBottom: 20, lineHeight: 1.6 }}>
            Supprimer{' '}
            <span style={{ fontFamily: "'Fira Code', monospace", color: '#E2E8F0', fontWeight: 500 }}>
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
        <FolderOpen className="w-6 h-6 text-dark-500" />
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
          Aucun projet défini
        </p>
        <p style={{ fontSize: 13, color: '#475569' }}>
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

  const initial = project.name.charAt(0).toUpperCase()

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
        el.style.boxShadow = '0 2px 12px rgba(0,0,0,0.35), 0 0 20px rgba(14, 165, 233, 0.06)'
      }}
      onMouseLeave={e => {
        const el = e.currentTarget
        el.style.borderLeftColor = 'rgba(14, 165, 233, 0.6)'
        el.style.background = 'rgba(10, 23, 40, 0.85)'
        el.style.boxShadow = '0 1px 3px rgba(0,0,0,0.3)'
      }}
    >
      {/* Avatar */}
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
        fontFamily: "'IBM Plex Mono', monospace",
        fontWeight: 600,
        fontSize: 15,
        color: '#38BDF8',
      }}>
        {initial}
      </div>

      {/* Name + date */}
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
          {project.name}
        </p>
        <p style={{ fontSize: 11, color: '#64748B', letterSpacing: '0.02em' }}>
          {date}
        </p>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
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
            const el = e.currentTarget
            el.style.color = '#FB7185'
            el.style.background = 'rgba(244, 63, 94, 0.1)'
          }}
          onMouseLeave={e => {
            const el = e.currentTarget
            el.style.color = '#475569'
            el.style.background = 'transparent'
          }}
        >
          <Trash2 style={{ width: 13, height: 13 }} />
        </button>

        <Link
          to={`/projects/${project.id}`}
          style={{
            width: 30,
            height: 30,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: 6,
            background: 'rgba(14, 165, 233, 0.1)',
            border: '1px solid rgba(14, 165, 233, 0.18)',
            color: '#38BDF8',
            transition: 'all 0.15s',
            textDecoration: 'none',
          }}
          onMouseEnter={e => {
            const el = e.currentTarget
            el.style.background = 'rgba(14, 165, 233, 0.18)'
            el.style.boxShadow = '0 0 12px rgba(14, 165, 233, 0.2)'
          }}
          onMouseLeave={e => {
            const el = e.currentTarget
            el.style.background = 'rgba(14, 165, 233, 0.1)'
            el.style.boxShadow = 'none'
          }}
        >
          <ArrowRight style={{ width: 13, height: 13 }} />
        </Link>
      </div>
    </div>
  )
}

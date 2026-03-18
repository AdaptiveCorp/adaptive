import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Plus,
  FolderOpen,
  Trash2,
  Server,
  Users,
  TreePine,
  ShieldAlert,
  Calendar,
} from 'lucide-react'
import { projectsApi } from '../api/projects'
import { Modal } from '../components/Modal'
import { Spinner } from '../components/Spinner'
import type { Project } from '../types'

export function ProjectsPage() {
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null)

  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list(),
  })

  const createMutation = useMutation({
    mutationFn: (name: string) => projectsApi.create(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setShowCreate(false)
      setNewName('')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => projectsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setDeleteTarget(null)
    },
  })

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (newName.trim()) createMutation.mutate(newName.trim())
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Projets</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Gérez vos labs Active Directory
          </p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Nouveau projet
        </button>
      </div>

      {/* Projects grid */}
      {isLoading ? (
        <div className="flex items-center justify-center py-24">
          <Spinner className="w-8 h-8 text-brand-400" />
        </div>
      ) : !projects?.length ? (
        <div className="card flex flex-col items-center justify-center py-24 gap-4 text-center">
          <FolderOpen className="w-12 h-12 text-slate-600" />
          <div>
            <p className="text-slate-300 font-medium">Aucun projet</p>
            <p className="text-slate-500 text-sm mt-1">
              Créez votre premier lab AD.
            </p>
          </div>
          <button onClick={() => setShowCreate(true)} className="btn-primary">
            Créer un projet
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onDelete={() => setDeleteTarget(project)}
            />
          ))}
        </div>
      )}

      {/* Create modal */}
      {showCreate && (
        <Modal title="Nouveau projet" onClose={() => setShowCreate(false)}>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">Nom du projet</label>
              <input
                className="input"
                placeholder="ex: lab-ctf-2026"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                autoFocus
              />
            </div>
            <div className="flex gap-2 justify-end pt-1">
              <button type="button" className="btn-ghost" onClick={() => setShowCreate(false)}>
                Annuler
              </button>
              <button
                type="submit"
                className="btn-primary flex items-center gap-2"
                disabled={!newName.trim() || createMutation.isPending}
              >
                {createMutation.isPending && <Spinner className="w-4 h-4" />}
                Créer
              </button>
            </div>
            {createMutation.isError && (
              <p className="text-danger-400 text-sm">Erreur lors de la création.</p>
            )}
          </form>
        </Modal>
      )}

      {/* Delete confirm modal */}
      {deleteTarget && (
        <Modal title="Supprimer le projet" onClose={() => setDeleteTarget(null)}>
          <p className="text-slate-300 text-sm">
            Supprimer <span className="font-semibold text-slate-100">{deleteTarget.name}</span> ?
            Cette action est irréversible.
          </p>
          <div className="flex gap-2 justify-end mt-5">
            <button className="btn-ghost" onClick={() => setDeleteTarget(null)}>
              Annuler
            </button>
            <button
              className="btn-danger flex items-center gap-2"
              disabled={deleteMutation.isPending}
              onClick={() => deleteMutation.mutate(deleteTarget.id)}
            >
              {deleteMutation.isPending && <Spinner className="w-4 h-4" />}
              Supprimer
            </button>
          </div>
        </Modal>
      )}
    </div>
  )
}

// ---- Sub-component ----

interface ProjectCardProps {
  project: Project
  onDelete: () => void
}

function ProjectCard({ project, onDelete }: ProjectCardProps) {
  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }

  return (
    <div className="card group flex flex-col gap-4 hover:border-dark-500 transition">
      {/* Top row */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-brand-600/20 flex items-center justify-center shrink-0">
            <FolderOpen className="w-4 h-4 text-brand-400" />
          </div>
          <div className="min-w-0">
            <h2 className="font-semibold text-slate-100 truncate">{project.name}</h2>
            <div className="flex items-center gap-1 text-xs text-slate-500 mt-0.5">
              <Calendar className="w-3 h-3" />
              {formatDate(project.created_at)}
            </div>
          </div>
        </div>
        <button
          onClick={(e) => {
            e.preventDefault()
            onDelete()
          }}
          className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-danger-400 transition"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Quick stats row */}
      <div className="grid grid-cols-4 gap-2">
        <StatChip icon={<TreePine className="w-3.5 h-3.5" />} label="Forêts" />
        <StatChip icon={<ShieldAlert className="w-3.5 h-3.5" />} label="Domaines" />
        <StatChip icon={<Server className="w-3.5 h-3.5" />} label="Serveurs" />
        <StatChip icon={<Users className="w-3.5 h-3.5" />} label="Users" />
      </div>

      {/* Link */}
      <Link
        to={`/projects/${project.id}`}
        className="btn-ghost text-center text-xs font-medium mt-auto"
      >
        Ouvrir →
      </Link>
    </div>
  )
}

function StatChip({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div className="flex flex-col items-center gap-1 bg-dark-700 rounded-lg p-2">
      <div className="text-slate-500">{icon}</div>
      <span className="text-xs text-slate-500">{label}</span>
    </div>
  )
}

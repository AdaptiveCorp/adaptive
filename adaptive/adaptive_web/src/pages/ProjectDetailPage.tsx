import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  ArrowLeft,
  Rocket,
  TreePine,
  Network,
  Server,
  Users,
  ShieldAlert,
  CheckCircle,
  XCircle,
  Calendar,
} from 'lucide-react'
import { projectsApi } from '../api/projects'
import { ADHierarchySection } from '../components/sections/ADHierarchySection'
import { UsersSection } from '../components/sections/UsersSection'
import { VulnerabilitiesSection } from '../components/sections/VulnerabilitiesSection'
import { Spinner } from '../components/Spinner'
import { Modal } from '../components/Modal'
import type { DeployResult } from '../types'

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const projectId = Number(id)

  const [deployResult, setDeployResult] = useState<DeployResult | null>(null)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId),
    enabled: !isNaN(projectId),
  })

  const deployMutation = useMutation({
    mutationFn: () => projectsApi.deploy(projectId),
    onSuccess: (result) => setDeployResult(result),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-32">
        <Spinner className="w-8 h-8 text-brand-400" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="card text-center py-16 space-y-3">
        <XCircle className="w-10 h-10 text-danger-400 mx-auto" />
        <p className="text-slate-300">Projet introuvable.</p>
        <Link to="/" className="btn-ghost inline-block">
          Retour aux projets
        </Link>
      </div>
    )
  }

  const { project, forests, domains, servers, users, vulnerabilities_count } = data

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    })
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb + header */}
      <div className="flex flex-col gap-1">
        <Link
          to="/"
          className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-300 transition w-fit"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Projets
        </Link>
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold text-slate-100">{project.name}</h1>
            <div className="flex items-center gap-1 text-sm text-slate-500 mt-0.5">
              <Calendar className="w-3.5 h-3.5" />
              Créé le {formatDate(project.created_at)}
            </div>
          </div>

          <button
            className="btn-primary flex items-center gap-2"
            onClick={() => deployMutation.mutate()}
            disabled={deployMutation.isPending || servers.length === 0}
            title={servers.length === 0 ? 'Ajoutez des serveurs avant de déployer' : undefined}
          >
            {deployMutation.isPending ? (
              <Spinner className="w-4 h-4" />
            ) : (
              <Rocket className="w-4 h-4" />
            )}
            {deployMutation.isPending ? 'Déploiement en cours…' : 'Déployer'}
          </button>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <StatCard
          icon={<TreePine className="w-5 h-5" />}
          label="Forêts"
          value={forests.length}
          color="text-brand-400"
        />
        <StatCard
          icon={<Network className="w-5 h-5" />}
          label="Domaines"
          value={domains.length}
          color="text-sky-400"
        />
        <StatCard
          icon={<Server className="w-5 h-5" />}
          label="Serveurs"
          value={servers.length}
          color="text-violet-400"
        />
        <StatCard
          icon={<Users className="w-5 h-5" />}
          label="Utilisateurs"
          value={users.length}
          color="text-emerald-400"
        />
        <StatCard
          icon={<ShieldAlert className="w-5 h-5" />}
          label="Vulnérabilités"
          value={vulnerabilities_count}
          color="text-danger-400"
        />
      </div>

      {/* Sections */}
      <ADHierarchySection
        projectId={projectId}
        forests={forests}
        domains={domains}
        servers={servers}
      />
      <UsersSection projectId={projectId} domains={domains} />
      <VulnerabilitiesSection projectId={projectId} />

      {/* Deploy result modal */}
      {deployResult && (
        <Modal title="Résultat du déploiement" onClose={() => setDeployResult(null)}>
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              {deployResult.deployment_result.success ? (
                <CheckCircle className="w-5 h-5 text-success-400 shrink-0" />
              ) : (
                <XCircle className="w-5 h-5 text-danger-400 shrink-0" />
              )}
              <span
                className={`font-medium ${
                  deployResult.deployment_result.success
                    ? 'text-success-400'
                    : 'text-danger-400'
                }`}
              >
                {deployResult.deployment_result.success ? 'Déploiement réussi' : 'Échec du déploiement'}
              </span>
            </div>

            {deployResult.deployment_result.message && (
              <p className="text-sm text-slate-300">{deployResult.deployment_result.message}</p>
            )}
            {deployResult.deployment_result.error && (
              <pre className="text-xs text-danger-400 bg-dark-700 rounded-lg p-3 overflow-auto max-h-40 font-mono">
                {deployResult.deployment_result.error}
              </pre>
            )}

            <div className="flex justify-end">
              <button className="btn-ghost" onClick={() => setDeployResult(null)}>
                Fermer
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}

// ---- Stat card ----
interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: number
  color: string
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  return (
    <div className="card flex items-center gap-3">
      <div className={`${color}`}>{icon}</div>
      <div>
        <p className="text-xl font-bold text-slate-100">{value}</p>
        <p className="text-xs text-slate-500">{label}</p>
      </div>
    </div>
  )
}

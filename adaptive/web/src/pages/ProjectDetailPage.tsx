import { useState } from 'react'
import { useParams, Link, useSearchParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  ArrowLeft, Rocket, LayoutDashboard, TreePine, Network,
  Server, Users, ShieldAlert, CheckCircle, XCircle,
} from 'lucide-react'
import { projectsApi }        from '../api/projects'
import { TabBar }             from '../components/tabs/TabBar'
import { DashboardTab }       from '../components/tabs/DashboardTab'
import { ForestsTab }         from '../components/tabs/ForestsTab'
import { DomainsTab }         from '../components/tabs/DomainsTab'
import { ServersTab }         from '../components/tabs/ServersTab'
import { UsersTab }           from '../components/tabs/UsersTab'
import { VulnerabilitiesTab } from '../components/tabs/VulnerabilitiesTab'
import { Spinner } from '../components/Spinner'
import { Modal }   from '../components/Modal'
import type { DeployResult } from '../types'

const TABS = [
  { id: 'dashboard',       label: 'Dashboard',      icon: <LayoutDashboard className="w-3.5 h-3.5" /> },
  { id: 'forests',         label: 'Forêts',         icon: <TreePine        className="w-3.5 h-3.5" /> },
  { id: 'domains',         label: 'Domaines',       icon: <Network         className="w-3.5 h-3.5" /> },
  { id: 'servers',         label: 'Serveurs',       icon: <Server          className="w-3.5 h-3.5" /> },
  { id: 'users',           label: 'Utilisateurs',   icon: <Users           className="w-3.5 h-3.5" /> },
  { id: 'vulnerabilities', label: 'Vulnérabilités', icon: <ShieldAlert     className="w-3.5 h-3.5" /> },
]

export function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const projectId = Number(id)
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const tab    = searchParams.get('tab') ?? 'dashboard'
  const setTab = (t: string) => navigate(`?tab=${t}`, { replace: true })
  const [deployResult, setDeployResult] = useState<DeployResult | null>(null)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId),
    enabled: !isNaN(projectId),
  })

  const deployMut = useMutation({
    mutationFn: () => projectsApi.deploy(projectId),
    onSuccess: (r) => setDeployResult(r),
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-32">
        <Spinner className="w-6 h-6 text-brand-400" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="card text-center py-16 space-y-3">
        <XCircle className="w-8 h-8 text-danger-400 mx-auto" />
        <p style={{ fontSize: 13, color: '#4B6480' }}>Projet introuvable.</p>
        <Link to="/" className="btn-ghost inline-flex mx-auto">
          <ArrowLeft className="w-4 h-4" /> Retour
        </Link>
      </div>
    )
  }

  const { project, forests, domains, servers, users, vulnerabilities_count } = data

  return (
    <div className="space-y-5">
      {/* Breadcrumb + header */}
      <div>
        <Link
          to="/"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 5,
            fontSize: 12,
            color: '#475569',
            textDecoration: 'none',
            marginBottom: 14,
            transition: 'color 0.15s',
            fontFamily: "'IBM Plex Mono', monospace",
            letterSpacing: '0.02em',
          }}
          onMouseEnter={e => { (e.currentTarget as HTMLAnchorElement).style.color = '#64748B' }}
          onMouseLeave={e => { (e.currentTarget as HTMLAnchorElement).style.color = '#475569' }}
        >
          <ArrowLeft style={{ width: 13, height: 13 }} />
          Projets
        </Link>

        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h1 style={{
              fontFamily: "'IBM Plex Mono', monospace",
              fontWeight: 600,
              fontSize: 20,
              color: '#E2E8F0',
              letterSpacing: '-0.02em',
              marginBottom: 3,
            }}>
              {project.name}
            </h1>
            <p style={{ fontSize: 12, color: '#475569', fontFamily: "'IBM Plex Mono', monospace" }}>
              ID: {project.id} · {new Date(project.created_at).toLocaleDateString('fr-FR', {
                day: '2-digit', month: 'long', year: 'numeric'
              })}
            </p>
          </div>

          <button
            className="btn-primary btn-deploy"
            onClick={() => deployMut.mutate()}
            disabled={deployMut.isPending || servers.length === 0}
            title={servers.length === 0 ? 'Ajoutez des serveurs avant de déployer' : undefined}
          >
            {deployMut.isPending
              ? <Spinner className="w-4 h-4" />
              : <Rocket className="w-4 h-4" />
            }
            {deployMut.isPending ? 'Déploiement…' : 'Déployer'}
          </button>
        </div>
      </div>

      {/* Tab bar */}
      <TabBar tabs={TABS} active={tab} onChange={setTab} />

      {/* Tab content */}
      <div>
        {tab === 'dashboard'       && <DashboardTab projectId={projectId} forests={forests} domains={domains} servers={servers} users={users} vulnerabilitiesCount={vulnerabilities_count} />}
        {tab === 'forests'         && <ForestsTab projectId={projectId} forests={forests} domains={domains} />}
        {tab === 'domains'         && <DomainsTab projectId={projectId} forests={forests} domains={domains} servers={servers} />}
        {tab === 'servers'         && <ServersTab projectId={projectId} domains={domains} servers={servers} />}
        {tab === 'users'           && <UsersTab projectId={projectId} domains={domains} />}
        {tab === 'vulnerabilities' && <VulnerabilitiesTab projectId={projectId} />}
      </div>

      {/* Deploy result */}
      {deployResult && (
        <Modal title="Résultat du déploiement" onClose={() => setDeployResult(null)}>
          <div className="space-y-3">
            <div className="flex items-center gap-2.5">
              {deployResult.deployment_result.success
                ? <CheckCircle className="w-5 h-5 text-success-400 shrink-0" />
                : <XCircle    className="w-5 h-5 text-danger-400 shrink-0" />
              }
              <span style={{
                fontSize: 14,
                fontWeight: 600,
                fontFamily: "'IBM Plex Mono', monospace",
                color: deployResult.deployment_result.success ? '#34D399' : '#FB7185',
              }}>
                {deployResult.deployment_result.success ? 'Déploiement réussi' : 'Échec du déploiement'}
              </span>
            </div>

            {deployResult.deployment_result.message && (
              <p style={{ fontSize: 13, color: '#94A3B8', lineHeight: 1.6 }}>
                {deployResult.deployment_result.message}
              </p>
            )}

            {deployResult.deployment_result.error && (
              <pre style={{
                fontSize: 11,
                color: '#FB7185',
                background: 'rgba(6, 16, 28, 0.8)',
                border: '1px solid rgba(22, 40, 64, 0.8)',
                borderRadius: 6,
                padding: '10px 12px',
                overflow: 'auto',
                maxHeight: 160,
                fontFamily: "'Fira Code', monospace",
              }}>
                {deployResult.deployment_result.error}
              </pre>
            )}

            <div className="flex justify-end pt-1">
              <button className="btn-ghost" onClick={() => setDeployResult(null)}>Fermer</button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}

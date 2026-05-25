import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ShieldAlert, Trash2, Plus, ArrowLeft, ChevronRight } from 'lucide-react'
import { vulnerabilitiesApi } from '../../api/vulnerabilities'
import { Badge } from '../Badge'
import { Spinner } from '../Spinner'
import { Modal } from '../Modal'
import type { AppliedVulnerability, Domain, User, Vulnerability } from '../../types'

interface Props {
  projectId: number
  domains: Domain[]
  users: User[]
}

const CATEGORY_VARIANT: Record<string, 'red' | 'yellow' | 'blue' | 'green' | 'gray'> = {
  kerberos:    'red',
  privilege:   'yellow',
  credential:  'red',
  acl:         'yellow',
  lateral:     'yellow',
  recon:       'blue',
  replication: 'red',
  account:     'blue',
  ldap:        'gray',
  misc:        'gray',
}

function categoryVariant(cat: string | null): 'red' | 'yellow' | 'blue' | 'green' | 'gray' {
  if (!cat) return 'gray'
  const key = Object.keys(CATEGORY_VARIANT).find(k => cat.toLowerCase().includes(k))
  return key ? CATEGORY_VARIANT[key] : 'gray'
}

function parseRequiredParams(raw: string | null | undefined): string[] {
  if (!raw) return []
  try {
    return JSON.parse(raw.replace(/'/g, '"'))
  } catch {
    return []
  }
}

function fqdnToDn(fqdn: string): string {
  return fqdn.split('.').map(p => `DC=${p}`).join(',')
}

const USERNAME_PARAMS = new Set(['username', 'source_username', 'target_username'])

// ─── Apply modal ────────────────────────────────────────────────────────────

interface ApplyModalProps {
  projectId: number
  domains: Domain[]
  users: User[]
  catalog: Vulnerability[]
  onClose: () => void
  onSuccess: () => void
}

function ApplyModal({ projectId, domains, users, catalog, onClose, onSuccess }: ApplyModalProps) {
  const [step, setStep] = useState<'pick' | 'configure'>('pick')
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<Vulnerability | null>(null)
  const [domainId, setDomainId] = useState<number>(domains[0]?.id ?? 0)
  const [params, setParams] = useState<Record<string, string>>({})

  const applyMut = useMutation({
    mutationFn: () =>
      vulnerabilitiesApi.apply(projectId, {
        vuln_id: selected!.id,
        domain_id: domainId,
        params,
      }),
    onSuccess,
  })

  function pickVuln(v: Vulnerability) {
    const reqParams = parseRequiredParams(v.required_params)
    const domain = domains.find(d => d.id === domainId) ?? domains[0]
    const initial: Record<string, string> = {}
    reqParams.forEach(p => {
      initial[p] = p === 'domain_dn' && domain ? fqdnToDn(domain.fqdn) : ''
    })
    setSelected(v)
    setParams(initial)
    setStep('configure')
  }

  function handleDomainChange(id: number) {
    setDomainId(id)
    const domain = domains.find(d => d.id === id)
    if (domain && selected) {
      const reqParams = parseRequiredParams(selected.required_params)
      setParams(prev => {
        const next = { ...prev }
        if (reqParams.includes('domain_dn')) {
          next['domain_dn'] = fqdnToDn(domain.fqdn)
        }
        return next
      })
    }
  }

  const domainUsers   = users.filter(u => u.domain_id === domainId)
  const reqParams     = selected ? parseRequiredParams(selected.required_params) : []
  const canSubmit     = selected && domainId && reqParams.every(p => params[p]?.trim())
  const filteredCatalog = catalog.filter(v =>
    v.name.toLowerCase().includes(search.toLowerCase()) ||
    v.code.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <Modal
      title={step === 'pick' ? 'Appliquer une vulnérabilité' : 'Configurer la vulnérabilité'}
      onClose={onClose}
    >
      {/* ── Step 1: pick ── */}
      {step === 'pick' && (
        <div className="space-y-3">
          <input
            className="input"
            placeholder="Rechercher par nom ou code…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            autoFocus
          />
          {catalog.length === 0 ? (
            <p style={{ fontSize: 13, color: 'var(--text-dim)', textAlign: 'center', padding: '24px 0' }}>
              Aucune vulnérabilité disponible dans le catalogue.
            </p>
          ) : filteredCatalog.length === 0 ? (
            <p style={{ fontSize: 13, color: 'var(--text-dim)', textAlign: 'center', padding: '24px 0' }}>
              Aucun résultat pour «&nbsp;{search}&nbsp;».
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 380, overflowY: 'auto' }}>
              {filteredCatalog.map(v => (
                <button
                  key={v.id}
                  onClick={() => pickVuln(v)}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: 12,
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-card)',
                    borderRadius: 8,
                    padding: '11px 14px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'border-color 0.15s',
                    width: '100%',
                  }}
                  onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--brand-400)' }}
                  onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-card)' }}
                >
                  <ShieldAlert style={{ width: 15, height: 15, color: '#FB7185', flexShrink: 0, marginTop: 2 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3, flexWrap: 'wrap' }}>
                      <Badge label={v.category ?? 'misc'} variant={categoryVariant(v.category)} />
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 13, fontWeight: 600, color: 'var(--text-bright)' }}>
                        {v.name}
                      </span>
                      <span style={{
                        fontFamily: "'Fira Code', monospace", fontSize: 10,
                        color: 'var(--text-dim)', background: 'var(--bg-input)',
                        border: '1px solid var(--border-input)', borderRadius: 4, padding: '1px 5px',
                      }}>
                        {v.code}
                      </span>
                    </div>
                    {v.description && (
                      <p style={{ fontSize: 12, color: 'var(--text-dim)', lineHeight: 1.4, margin: 0 }}>
                        {v.description}
                      </p>
                    )}
                  </div>
                  <ChevronRight style={{ width: 14, height: 14, color: 'var(--text-dim)', flexShrink: 0, marginTop: 3 }} />
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Step 2: configure ── */}
      {step === 'configure' && selected && (
        <form
          onSubmit={e => { e.preventDefault(); if (canSubmit) applyMut.mutate() }}
          className="space-y-4"
        >
          {/* Selected vuln recap */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 10,
            background: 'var(--bg-input)', border: '1px solid var(--border-input)',
            borderRadius: 8, padding: '10px 12px',
          }}>
            <ShieldAlert style={{ width: 14, height: 14, color: '#FB7185', flexShrink: 0 }} />
            <Badge label={selected.category ?? 'misc'} variant={categoryVariant(selected.category)} />
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 13, fontWeight: 600, color: 'var(--text-bright)', flex: 1 }}>
              {selected.name}
            </span>
            <button
              type="button"
              onClick={() => { setStep('pick'); setSelected(null) }}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-dim)', padding: 2, display: 'flex' }}
              title="Changer de vulnérabilité"
            >
              <ArrowLeft style={{ width: 14, height: 14 }} />
            </button>
          </div>

          {/* Domain */}
          <div>
            <label>Domaine cible</label>
            {domains.length === 0 ? (
              <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace" }}>
                Aucun domaine disponible.
              </p>
            ) : (
              <select
                className="input"
                value={domainId}
                onChange={e => handleDomainChange(Number(e.target.value))}
              >
                {domains.map(d => (
                  <option key={d.id} value={d.id}>{d.fqdn}</option>
                ))}
              </select>
            )}
          </div>

          {/* Dynamic params */}
          {reqParams.length > 0 && (
            <div className="space-y-3">
              <span style={{
                fontFamily: "'IBM Plex Mono', monospace", fontSize: 10, fontWeight: 600,
                color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em',
              }}>
                Paramètres
              </span>
              {reqParams.map(param => (
                <div key={param}>
                  <label style={{ textTransform: 'none' }}>
                    <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 12 }}>{param}</span>
                  </label>
                  {USERNAME_PARAMS.has(param) ? (
                    domainUsers.length > 0 ? (
                      <select
                        className="input"
                        value={params[param] ?? ''}
                        onChange={e => setParams({ ...params, [param]: e.target.value })}
                        required
                      >
                        <option value="">— Sélectionner un utilisateur —</option>
                        {domainUsers.map(u => (
                          <option key={u.id} value={u.username}>{u.username}</option>
                        ))}
                      </select>
                    ) : (
                      <input
                        className="input"
                        placeholder={`ex: j.doe`}
                        value={params[param] ?? ''}
                        onChange={e => setParams({ ...params, [param]: e.target.value })}
                        required
                      />
                    )
                  ) : (
                    <input
                      className="input"
                      placeholder={param === 'spn_name' ? 'ex: HTTP/myserver.corp.local' : param === 'domain_dn' ? 'ex: DC=corp,DC=local' : ''}
                      value={params[param] ?? ''}
                      onChange={e => setParams({ ...params, [param]: e.target.value })}
                      required
                    />
                  )}
                </div>
              ))}
            </div>
          )}

          {reqParams.length === 0 && (
            <p style={{ fontSize: 12, color: 'var(--text-dim)', fontFamily: "'IBM Plex Mono', monospace" }}>
              Cette vulnérabilité ne nécessite aucun paramètre.
            </p>
          )}

          <div className="flex gap-2 justify-end">
            <button type="button" className="btn-ghost" onClick={onClose}>Annuler</button>
            <button
              type="submit"
              className="btn-primary"
              disabled={!canSubmit || applyMut.isPending}
            >
              {applyMut.isPending && <Spinner className="w-3.5 h-3.5" />}
              Appliquer
            </button>
          </div>
          {applyMut.isError && (
            <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace" }}>
              Erreur lors de l'application (déjà appliquée avec ces paramètres ?).
            </p>
          )}
        </form>
      )}
    </Modal>
  )
}

// ─── Status badge ────────────────────────────────────────────────────────────

const STATUS_STYLE: Record<string, { color: string; bg: string; label: string }> = {
  pending:          { color: '#FBBF24', bg: 'rgba(251,191,36,0.1)',  label: 'en attente' },
  applied:          { color: '#4ADE80', bg: 'rgba(74,222,128,0.1)',  label: 'appliquée' },
  error:            { color: '#FB7185', bg: 'rgba(244,63,94,0.1)',   label: 'erreur' },
  reverted_pending: { color: '#94A3B8', bg: 'rgba(148,163,184,0.1)', label: 'revert en attente' },
  reverted_applied: { color: '#64748B', bg: 'rgba(100,116,139,0.1)', label: 'revertée' },
}

function StatusBadge({ status }: { status: string }) {
  const s = STATUS_STYLE[status] ?? STATUS_STYLE['pending']
  return (
    <span style={{
      fontFamily: "'IBM Plex Mono', monospace", fontSize: 10, fontWeight: 600,
      color: s.color, background: s.bg, borderRadius: 4, padding: '2px 7px',
      letterSpacing: '0.06em', textTransform: 'uppercase',
    }}>
      {s.label}
    </span>
  )
}

// ─── Main section ─────────────────────────────────────────────────────────────

export function VulnerabilitiesSection({ projectId, domains, users }: Props) {
  const queryClient = useQueryClient()
  const [showApply,    setShowApply]    = useState(false)
  const [removeTarget, setRemoveTarget] = useState<AppliedVulnerability | null>(null)

  const { data: applied, isLoading } = useQuery({
    queryKey: ['applied-vulns', projectId],
    queryFn:  () => vulnerabilitiesApi.listApplied(projectId),
  })

  const { data: catalog = [] } = useQuery({
    queryKey: ['vulnerabilities'],
    queryFn:  () => vulnerabilitiesApi.list(),
  })

  const removeMutation = useMutation({
    mutationFn: (id: number) => vulnerabilitiesApi.removeApplied(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applied-vulns', projectId] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      setRemoveTarget(null)
    },
  })

  const domainName = (id: number | null) =>
    id ? (domains.find(d => d.id === id)?.fqdn ?? `#${id}`) : null

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span style={{
          fontFamily: "'IBM Plex Mono', monospace", fontSize: 10, fontWeight: 600,
          color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em',
        }}>
          Vulnérabilités appliquées
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, color: 'var(--text-dim)' }}>
            {applied?.length ?? 0} / {catalog.length}
          </span>
          <button
            className="btn-ghost"
            style={{ padding: '5px 12px', fontSize: 12 }}
            onClick={() => setShowApply(true)}
            disabled={domains.length === 0}
            title={domains.length === 0 ? "Créez d'abord un domaine" : undefined}
          >
            <Plus className="w-3.5 h-3.5" /> Appliquer
          </button>
        </div>
      </div>

      {/* Applied list */}
      <div className="card space-y-3">
        {isLoading ? (
          <div className="flex justify-center py-6">
            <Spinner className="w-5 h-5 text-brand-400" />
          </div>
        ) : !applied?.length ? (
          <div style={{ textAlign: 'center', padding: '28px 0' }}>
            <ShieldAlert style={{ width: 28, height: 28, color: 'var(--text-dim)', margin: '0 auto 10px' }} />
            <p style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: 'var(--text-dim)' }}>
              Aucune vulnérabilité appliquée à ce projet.
            </p>
          </div>
        ) : (
          applied.map((av) => (
            <div
              key={av.id}
              style={{
                display: 'flex', alignItems: 'flex-start', gap: 12,
                background: 'var(--bg-card)', border: '1px solid var(--border-card)',
                borderRadius: 8, padding: '12px 14px',
              }}
              className="group"
            >
              <ShieldAlert style={{ width: 15, height: 15, color: '#FB7185', marginTop: 2, flexShrink: 0 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 5 }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-bright)' }}>
                    {av.template.name}
                  </span>
                  <span style={{
                    fontFamily: "'Fira Code', monospace", fontSize: 10,
                    color: 'var(--text-dim)', background: 'var(--bg-input)',
                    border: '1px solid var(--border-input)', borderRadius: 4, padding: '1px 5px',
                  }}>
                    {av.template.code}
                  </span>
                  <StatusBadge status={av.status} />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                  {av.domain_id && <Badge label={domainName(av.domain_id) ?? `Domain #${av.domain_id}`} variant="blue" />}
                  {av.user_id   && <Badge label={`User #${av.user_id}`}   variant="yellow" />}
                  {av.server_id && <Badge label={`Server #${av.server_id}`} variant="gray" />}
                  {av.forest_id && <Badge label={`Forest #${av.forest_id}`} variant="green" />}
                </div>
                {av.params && (
                  <pre style={{
                    fontFamily: "'Fira Code', monospace", fontSize: 11, color: 'var(--text-dim)',
                    marginTop: 6, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                  }}>
                    {av.params}
                  </pre>
                )}
                <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4, fontFamily: "'IBM Plex Mono', monospace" }}>
                  {new Date(av.created_at).toLocaleDateString('fr-FR')}
                </p>
              </div>
              <button
                onClick={() => setRemoveTarget(av)}
                className="row-del"
                style={{ opacity: 0, flexShrink: 0 }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.opacity = '1' }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.opacity = '0' }}
              >
                <Trash2 style={{ width: 14, height: 14 }} />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Apply modal */}
      {showApply && (
        <ApplyModal
          projectId={projectId}
          domains={domains}
          users={users}
          catalog={catalog}
          onClose={() => setShowApply(false)}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['applied-vulns', projectId] })
            queryClient.invalidateQueries({ queryKey: ['project', projectId] })
            setShowApply(false)
          }}
        />
      )}

      {/* Remove confirm */}
      {removeTarget && (
        <Modal title="Retirer la vulnérabilité" onClose={() => setRemoveTarget(null)}>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 20, lineHeight: 1.6 }}>
            Retirer{' '}
            <span style={{ fontFamily: "'Fira Code', monospace", color: 'var(--text-bright)', fontWeight: 500 }}>
              {removeTarget.template.name}
            </span>{' '}
            de ce projet ?
          </p>
          <div className="flex gap-2 justify-end">
            <button className="btn-ghost" onClick={() => setRemoveTarget(null)}>Annuler</button>
            <button className="btn-danger" disabled={removeMutation.isPending}
              onClick={() => removeMutation.mutate(removeTarget.id)}>
              {removeMutation.isPending && <Spinner className="w-4 h-4" />}
              Retirer
            </button>
          </div>
          {removeMutation.isError && (
            <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace", marginTop: 12 }}>
              Impossible de retirer cette vulnérabilité.
            </p>
          )}
        </Modal>
      )}
    </div>
  )
}

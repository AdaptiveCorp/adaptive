import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ChevronRight, Server, Plus, Cpu, Network, TreePine } from 'lucide-react'
import { forestsApi } from '../../api/forests'
import { domainsApi } from '../../api/domains'
import { serversApi } from '../../api/servers'
import { Modal } from '../Modal'
import { Badge } from '../Badge'
import { Spinner } from '../Spinner'
import type { Forest, Domain, Server as ServerType } from '../../types'

interface Props {
  projectId: number
  forests: Forest[]
  domains: Domain[]
  servers: ServerType[]
}

export function ADHierarchySection({ projectId, forests, domains, servers }: Props) {
  const queryClient = useQueryClient()
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['project', projectId] })

  const [addForestOpen, setAddForestOpen] = useState(false)
  const [addDomainTarget, setAddDomainTarget] = useState<Forest | null>(null)
  const [addServerTarget, setAddServerTarget] = useState<Domain | null>(null)

  const [openForests, setOpenForests] = useState<Set<number>>(new Set(forests.map((f) => f.id)))
  const [openDomains, setOpenDomains] = useState<Set<number>>(new Set(domains.map((d) => d.id)))

  const [forestFqdn, setForestFqdn] = useState('')
  const [domainFqdn, setDomainFqdn] = useState('')
  const [serverForm, setServerForm] = useState({ fqdn: '', is_dc: false, ip: '', gtw: '', dns: '' })

  const addForestMutation = useMutation({
    mutationFn: (fqdn: string) => forestsApi.create(projectId, fqdn),
    onSuccess: (newForest) => {
      setOpenForests((prev) => new Set([...prev, newForest.id]))
      invalidate(); setAddForestOpen(false); setForestFqdn('')
    },
  })

  const addDomainMutation = useMutation({
    mutationFn: ({ forestId, fqdn }: { forestId: number; fqdn: string }) => domainsApi.create(forestId, fqdn),
    onSuccess: (newDomain) => {
      setOpenDomains((prev) => new Set([...prev, newDomain.id]))
      invalidate(); setAddDomainTarget(null); setDomainFqdn('')
    },
  })

  const addServerMutation = useMutation({
    mutationFn: ({ domainId, form }: { domainId: number; form: typeof serverForm }) =>
      serversApi.create(domainId, { fqdn: form.fqdn, is_dc: form.is_dc, ip: form.ip || undefined, gtw: form.gtw || undefined, dns: form.dns || undefined }),
    onSuccess: (_data, variables) => {
      setOpenDomains((prev) => new Set([...prev, variables.domainId]))
      invalidate(); setAddServerTarget(null)
      setServerForm({ fqdn: '', is_dc: false, ip: '', gtw: '', dns: '' })
    },
  })

  const domainsForForest = (forestId: number) => domains.filter((d) => d.forest_id === forestId)
  const serversForDomain = (domainId: number) => servers.filter((s) => s.domain_id === domainId)

  const toggleForest = (id: number) => setOpenForests((prev) => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n })
  const toggleDomain = (id: number) => setOpenDomains((prev) => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n })

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <span style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 10,
          fontWeight: 600,
          color: '#475569',
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
        }}>
          Hiérarchie Active Directory
        </span>
        <button className="btn-ghost" style={{ padding: '5px 12px', fontSize: 12 }} onClick={() => setAddForestOpen(true)}>
          <Plus className="w-3.5 h-3.5" /> Forêt
        </button>
      </div>

      {forests.length === 0 && (
        <p style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: '#475569', textAlign: 'center', padding: '24px 0' }}>
          Aucune forêt — ajoutez-en une pour commencer.
        </p>
      )}

      {forests.map((forest) => (
        <div key={forest.id} style={{
          background: 'rgba(15, 32, 52, 0.6)',
          border: '1px solid rgba(22, 40, 64, 0.8)',
          borderRadius: 8,
          overflow: 'hidden',
        }}>
          <button
            onClick={() => toggleForest(forest.id)}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 14px',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              transition: 'background 0.15s',
              textAlign: 'left',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(22, 40, 64, 0.5)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'transparent' }}
          >
            <ChevronRight style={{
              width: 14, height: 14, color: '#64748B', flexShrink: 0,
              transform: openForests.has(forest.id) ? 'rotate(90deg)' : 'none',
              transition: 'transform 0.15s',
            }} />
            <TreePine style={{ width: 14, height: 14, color: '#38BDF8', flexShrink: 0 }} />
            <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 13, color: '#CBD5E1', flex: 1 }}>
              {forest.fqdn}
            </span>
            <Badge label="Forêt" variant="blue" />
          </button>

          {openForests.has(forest.id) && (
            <div style={{ padding: '0 14px 12px', display: 'flex', flexDirection: 'column', gap: 6 }}>
              {domainsForForest(forest.id).map((domain) => (
                <div key={domain.id} style={{
                  marginLeft: 22,
                  background: 'rgba(10, 23, 40, 0.7)',
                  border: '1px solid rgba(22, 40, 64, 0.7)',
                  borderRadius: 7,
                  overflow: 'hidden',
                }}>
                  <button
                    onClick={() => toggleDomain(domain.id)}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      padding: '8px 12px',
                      background: 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                      transition: 'background 0.15s',
                      textAlign: 'left',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = 'rgba(22, 40, 64, 0.4)' }}
                    onMouseLeave={e => { e.currentTarget.style.background = 'transparent' }}
                  >
                    <ChevronRight style={{
                      width: 13, height: 13, color: '#64748B', flexShrink: 0,
                      transform: openDomains.has(domain.id) ? 'rotate(90deg)' : 'none',
                      transition: 'transform 0.15s',
                    }} />
                    <Network style={{ width: 13, height: 13, color: '#818CF8', flexShrink: 0 }} />
                    <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 13, color: '#94A3B8', flex: 1 }}>
                      {domain.fqdn}
                    </span>
                    <Badge label="Domaine" variant="gray" />
                  </button>

                  {openDomains.has(domain.id) && (
                    <div style={{ padding: '0 12px 10px', marginLeft: 20, display: 'flex', flexDirection: 'column', gap: 4 }}>
                      {serversForDomain(domain.id).map((server) => (
                        <div key={server.id} style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 8,
                          padding: '7px 10px',
                          background: 'rgba(15, 32, 52, 0.5)',
                          border: '1px solid rgba(22, 40, 64, 0.6)',
                          borderRadius: 6,
                        }}>
                          <Server style={{ width: 12, height: 12, color: '#34D399', flexShrink: 0 }} />
                          <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 12, color: '#94A3B8', flex: 1 }}>
                            {server.fqdn}
                          </span>
                          {server.ip && (
                            <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 11, color: '#64748B' }}>
                              {server.ip}
                            </span>
                          )}
                          {server.vm_id && (
                            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 10, color: '#475569' }}>
                              VM#{server.vm_id}
                            </span>
                          )}
                          <Badge label={server.is_dc ? 'DC' : 'Serveur'} variant={server.is_dc ? 'green' : 'gray'} />
                        </div>
                      ))}
                      <button
                        onClick={() => setAddServerTarget(domain)}
                        style={{
                          display: 'flex', alignItems: 'center', gap: 5,
                          padding: '6px 10px', fontSize: 12,
                          color: '#475569', background: 'none', border: 'none',
                          cursor: 'pointer', borderRadius: 5, transition: 'all 0.15s',
                          fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                        }}
                        onMouseEnter={e => { e.currentTarget.style.color = '#38BDF8'; e.currentTarget.style.background = 'rgba(14, 165, 233, 0.06)' }}
                        onMouseLeave={e => { e.currentTarget.style.color = '#475569'; e.currentTarget.style.background = 'none' }}
                      >
                        <Plus style={{ width: 11, height: 11 }} /> Ajouter un serveur
                      </button>
                    </div>
                  )}
                </div>
              ))}

              <button
                onClick={() => setAddDomainTarget(forest)}
                style={{
                  marginLeft: 22,
                  display: 'flex', alignItems: 'center', gap: 5,
                  padding: '6px 10px', fontSize: 12,
                  color: '#475569', background: 'none', border: 'none',
                  cursor: 'pointer', borderRadius: 5, transition: 'all 0.15s',
                  fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
                }}
                onMouseEnter={e => { e.currentTarget.style.color = '#38BDF8'; e.currentTarget.style.background = 'rgba(14, 165, 233, 0.06)' }}
                onMouseLeave={e => { e.currentTarget.style.color = '#475569'; e.currentTarget.style.background = 'none' }}
              >
                <Plus style={{ width: 11, height: 11 }} /> Ajouter un domaine
              </button>
            </div>
          )}
        </div>
      ))}

      {/* Modals */}
      {addForestOpen && (
        <Modal title="Nouvelle forêt" onClose={() => setAddForestOpen(false)}>
          <form onSubmit={(e) => { e.preventDefault(); if (forestFqdn.trim()) addForestMutation.mutate(forestFqdn.trim()) }} className="space-y-4">
            <div>
              <label>FQDN de la forêt</label>
              <input className="input" placeholder="ex: corp.local" value={forestFqdn} onChange={(e) => setForestFqdn(e.target.value)} autoFocus />
            </div>
            <div className="flex gap-2 justify-end">
              <button type="button" className="btn-ghost" onClick={() => setAddForestOpen(false)}>Annuler</button>
              <button type="submit" className="btn-primary" disabled={!forestFqdn.trim() || addForestMutation.isPending}>
                {addForestMutation.isPending && <Spinner className="w-4 h-4" />} Ajouter
              </button>
            </div>
          </form>
        </Modal>
      )}

      {addDomainTarget && (
        <Modal title={`Nouveau domaine — ${addDomainTarget.fqdn}`} onClose={() => setAddDomainTarget(null)}>
          <form onSubmit={(e) => { e.preventDefault(); if (domainFqdn.trim()) addDomainMutation.mutate({ forestId: addDomainTarget.id, fqdn: domainFqdn.trim() }) }} className="space-y-4">
            <div>
              <label>FQDN du domaine</label>
              <input className="input" placeholder="ex: sub.corp.local" value={domainFqdn} onChange={(e) => setDomainFqdn(e.target.value)} autoFocus />
            </div>
            <div className="flex gap-2 justify-end">
              <button type="button" className="btn-ghost" onClick={() => setAddDomainTarget(null)}>Annuler</button>
              <button type="submit" className="btn-primary" disabled={!domainFqdn.trim() || addDomainMutation.isPending}>
                {addDomainMutation.isPending && <Spinner className="w-4 h-4" />} Ajouter
              </button>
            </div>
          </form>
        </Modal>
      )}

      {addServerTarget && (
        <Modal title={`Nouveau serveur — ${addServerTarget.fqdn}`} onClose={() => setAddServerTarget(null)}>
          <form onSubmit={(e) => { e.preventDefault(); if (serverForm.fqdn.trim()) addServerMutation.mutate({ domainId: addServerTarget.id, form: serverForm }) }} className="space-y-3">
            <div>
              <label>FQDN</label>
              <input className="input" placeholder="ex: dc01.sub.corp.local" value={serverForm.fqdn} onChange={(e) => setServerForm({ ...serverForm, fqdn: e.target.value })} autoFocus />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label>IP</label>
                <input className="input" placeholder="192.168.x.x" value={serverForm.ip} onChange={(e) => setServerForm({ ...serverForm, ip: e.target.value })} />
              </div>
              <div>
                <label>Passerelle</label>
                <input className="input" placeholder="192.168.x.1" value={serverForm.gtw} onChange={(e) => setServerForm({ ...serverForm, gtw: e.target.value })} />
              </div>
            </div>
            <div>
              <label>DNS</label>
              <input className="input" placeholder="192.168.x.x" value={serverForm.dns} onChange={(e) => setServerForm({ ...serverForm, dns: e.target.value })} />
            </div>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', userSelect: 'none', textTransform: 'none', letterSpacing: 0, marginBottom: 0 }}>
              <input type="checkbox" checked={serverForm.is_dc} onChange={(e) => setServerForm({ ...serverForm, is_dc: e.target.checked })} />
              <span style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 13, color: '#94A3B8', fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif", fontWeight: 500 }}>
                <Cpu style={{ width: 13, height: 13, color: '#34D399' }} /> Domain Controller
              </span>
            </label>
            <div className="flex gap-2 justify-end pt-1">
              <button type="button" className="btn-ghost" onClick={() => setAddServerTarget(null)}>Annuler</button>
              <button type="submit" className="btn-primary" disabled={!serverForm.fqdn.trim() || addServerMutation.isPending}>
                {addServerMutation.isPending && <Spinner className="w-4 h-4" />} Ajouter
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}

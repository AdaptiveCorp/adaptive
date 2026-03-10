import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ChevronRight, Server, Plus, Cpu, Network } from 'lucide-react'
import { forestsApi } from '../../api/forests'
import { domainsApi } from '../../api/domains'
import { serversApi } from '../../api/servers'
import { Modal } from '../Modal'
import { Badge } from '../Badge'
import { Spinner } from '../Spinner'
import type { Forest, Domain, Server as ServerType } from '../../types'

// ---- State helpers ----
interface Props {
  projectId: number
  forests: Forest[]
  domains: Domain[]
  servers: ServerType[]
}

export function ADHierarchySection({ projectId, forests, domains, servers }: Props) {
  const queryClient = useQueryClient()
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['project', projectId] })

  // Modals
  const [addForestOpen, setAddForestOpen] = useState(false)
  const [addDomainTarget, setAddDomainTarget] = useState<Forest | null>(null)
  const [addServerTarget, setAddServerTarget] = useState<Domain | null>(null)

  // Expand/collapse: forests open by default
  const [openForests, setOpenForests] = useState<Set<number>>(new Set(forests.map((f) => f.id)))
  const [openDomains, setOpenDomains] = useState<Set<number>>(new Set(domains.map((d) => d.id)))

  // Forms
  const [forestFqdn, setForestFqdn] = useState('')
  const [domainFqdn, setDomainFqdn] = useState('')
  const [serverForm, setServerForm] = useState({
    fqdn: '',
    is_dc: false,
    ip: '',
    gtw: '',
    dns: '',
  })

  const addForestMutation = useMutation({
    mutationFn: (fqdn: string) => forestsApi.create(projectId, fqdn),
    onSuccess: (newForest) => {
      setOpenForests((prev) => new Set([...prev, newForest.id]))
      invalidate()
      setAddForestOpen(false)
      setForestFqdn('')
    },
  })

  const addDomainMutation = useMutation({
    mutationFn: ({ forestId, fqdn }: { forestId: number; fqdn: string }) =>
      domainsApi.create(forestId, fqdn),
    onSuccess: (newDomain) => {
      setOpenDomains((prev) => new Set([...prev, newDomain.id]))
      invalidate()
      setAddDomainTarget(null)
      setDomainFqdn('')
    },
  })

  const addServerMutation = useMutation({
    mutationFn: ({
      domainId,
      form,
    }: {
      domainId: number
      form: typeof serverForm
    }) =>
      serversApi.create(domainId, {
        fqdn: form.fqdn,
        is_dc: form.is_dc,
        ip: form.ip || undefined,
        gtw: form.gtw || undefined,
        dns: form.dns || undefined,
      }),
    onSuccess: (_data, variables) => {
      // S'assurer que le domaine parent est bien déplié
      setOpenDomains((prev) => new Set([...prev, variables.domainId]))
      invalidate()
      setAddServerTarget(null)
      setServerForm({ fqdn: '', is_dc: false, ip: '', gtw: '', dns: '' })
    },
  })

  const domainsForForest = (forestId: number) => domains.filter((d) => d.forest_id === forestId)
  const serversForDomain = (domainId: number) => servers.filter((s) => s.domain_id === domainId)

  const toggleForest = (id: number) =>
    setOpenForests((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })

  const toggleDomain = (id: number) =>
    setOpenDomains((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })

  return (
    <div className="card space-y-3">
      {/* Section header */}
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Hiérarchie Active Directory
        </h2>
        <button
          className="btn-ghost text-xs flex items-center gap-1"
          onClick={() => setAddForestOpen(true)}
        >
          <Plus className="w-3.5 h-3.5" /> Forêt
        </button>
      </div>

      {forests.length === 0 && (
        <p className="text-slate-500 text-sm py-4 text-center">
          Aucune forêt — ajoutez-en une pour commencer.
        </p>
      )}

      {/* Forest tree */}
      {forests.map((forest) => (
        <div key={forest.id} className="bg-dark-700 rounded-xl overflow-hidden">
          {/* Forest row */}
          <button
            onClick={() => toggleForest(forest.id)}
            className="w-full flex items-center gap-2 px-4 py-2.5 hover:bg-dark-600 transition text-left"
          >
            <ChevronRight
              className={`w-4 h-4 text-slate-400 transition-transform ${
                openForests.has(forest.id) ? 'rotate-90' : ''
              }`}
            />
            <Network className="w-4 h-4 text-brand-400" />
            <span className="text-sm font-medium text-slate-200 flex-1">{forest.fqdn}</span>
            <Badge label="Forêt" variant="blue" />
          </button>

          {/* Domains */}
          {openForests.has(forest.id) && (
            <div className="px-4 pb-3 space-y-2">
              {domainsForForest(forest.id).map((domain) => (
                <div key={domain.id} className="bg-dark-800 rounded-lg overflow-hidden ml-6">
                  {/* Domain row */}
                  <button
                    onClick={() => toggleDomain(domain.id)}
                    className="w-full flex items-center gap-2 px-3 py-2 hover:bg-dark-600 transition text-left"
                  >
                    <ChevronRight
                      className={`w-3.5 h-3.5 text-slate-400 transition-transform ${
                        openDomains.has(domain.id) ? 'rotate-90' : ''
                      }`}
                    />
                    <Network className="w-3.5 h-3.5 text-brand-400/70" />
                    <span className="text-sm text-slate-300 flex-1">{domain.fqdn}</span>
                    <Badge label="Domaine" variant="gray" />
                  </button>

                  {/* Servers */}
                  {openDomains.has(domain.id) && (
                    <div className="px-3 pb-3 space-y-1 ml-5">
                      {serversForDomain(domain.id).map((server) => (
                        <div
                          key={server.id}
                          className="flex items-center gap-2 px-3 py-2 bg-dark-700 rounded-lg"
                        >
                          <Server className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span className="text-xs text-slate-300 flex-1 font-mono">
                            {server.fqdn}
                          </span>
                          {server.ip && (
                            <span className="text-xs text-slate-500 font-mono">{server.ip}</span>
                          )}
                          {server.vm_id && (
                            <span className="text-xs text-slate-600 font-mono">
                              VM#{server.vm_id}
                            </span>
                          )}
                          <Badge
                            label={server.is_dc ? 'DC' : 'Serveur'}
                            variant={server.is_dc ? 'green' : 'gray'}
                          />
                        </div>
                      ))}

                      {/* Add server btn */}
                      <button
                        onClick={() => setAddServerTarget(domain)}
                        className="w-full flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-500
                          hover:text-brand-400 hover:bg-dark-600 rounded-lg transition"
                      >
                        <Plus className="w-3 h-3" /> Ajouter un serveur
                      </button>
                    </div>
                  )}
                </div>
              ))}

              {/* Add domain btn */}
              <button
                onClick={() => setAddDomainTarget(forest)}
                className="ml-6 flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-500
                  hover:text-brand-400 hover:bg-dark-600 rounded-lg transition"
              >
                <Plus className="w-3 h-3" /> Ajouter un domaine
              </button>
            </div>
          )}
        </div>
      ))}

      {/* ---- Modals ---- */}

      {/* Add Forest */}
      {addForestOpen && (
        <Modal title="Nouvelle forêt" onClose={() => setAddForestOpen(false)}>
          <form
            onSubmit={(e) => {
              e.preventDefault()
              if (forestFqdn.trim()) addForestMutation.mutate(forestFqdn.trim())
            }}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">FQDN de la forêt</label>
              <input
                className="input"
                placeholder="ex: corp.local"
                value={forestFqdn}
                onChange={(e) => setForestFqdn(e.target.value)}
                autoFocus
              />
            </div>
            <div className="flex gap-2 justify-end">
              <button type="button" className="btn-ghost" onClick={() => setAddForestOpen(false)}>
                Annuler
              </button>
              <button
                type="submit"
                className="btn-primary flex items-center gap-2"
                disabled={!forestFqdn.trim() || addForestMutation.isPending}
              >
                {addForestMutation.isPending && <Spinner className="w-4 h-4" />}
                Ajouter
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Add Domain */}
      {addDomainTarget && (
        <Modal
          title={`Nouveau domaine dans ${addDomainTarget.fqdn}`}
          onClose={() => setAddDomainTarget(null)}
        >
          <form
            onSubmit={(e) => {
              e.preventDefault()
              if (domainFqdn.trim())
                addDomainMutation.mutate({ forestId: addDomainTarget.id, fqdn: domainFqdn.trim() })
            }}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">FQDN du domaine</label>
              <input
                className="input"
                placeholder="ex: sub.corp.local"
                value={domainFqdn}
                onChange={(e) => setDomainFqdn(e.target.value)}
                autoFocus
              />
            </div>
            <div className="flex gap-2 justify-end">
              <button type="button" className="btn-ghost" onClick={() => setAddDomainTarget(null)}>
                Annuler
              </button>
              <button
                type="submit"
                className="btn-primary flex items-center gap-2"
                disabled={!domainFqdn.trim() || addDomainMutation.isPending}
              >
                {addDomainMutation.isPending && <Spinner className="w-4 h-4" />}
                Ajouter
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Add Server */}
      {addServerTarget && (
        <Modal
          title={`Nouveau serveur dans ${addServerTarget.fqdn}`}
          onClose={() => setAddServerTarget(null)}
        >
          <form
            onSubmit={(e) => {
              e.preventDefault()
              if (serverForm.fqdn.trim())
                addServerMutation.mutate({ domainId: addServerTarget.id, form: serverForm })
            }}
            className="space-y-3"
          >
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">FQDN</label>
              <input
                className="input"
                placeholder="ex: dc01.sub.corp.local"
                value={serverForm.fqdn}
                onChange={(e) => setServerForm({ ...serverForm, fqdn: e.target.value })}
                autoFocus
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm text-slate-400 mb-1.5">IP</label>
                <input
                  className="input"
                  placeholder="192.168.x.x"
                  value={serverForm.ip}
                  onChange={(e) => setServerForm({ ...serverForm, ip: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1.5">Passerelle</label>
                <input
                  className="input"
                  placeholder="192.168.x.1"
                  value={serverForm.gtw}
                  onChange={(e) => setServerForm({ ...serverForm, gtw: e.target.value })}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">DNS</label>
              <input
                className="input"
                placeholder="192.168.x.x"
                value={serverForm.dns}
                onChange={(e) => setServerForm({ ...serverForm, dns: e.target.value })}
              />
            </div>
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={serverForm.is_dc}
                onChange={(e) => setServerForm({ ...serverForm, is_dc: e.target.checked })}
                className="rounded"
              />
              <span className="flex items-center gap-1.5 text-sm text-slate-300">
                <Cpu className="w-3.5 h-3.5 text-success-400" /> Domain Controller
              </span>
            </label>
            <div className="flex gap-2 justify-end pt-1">
              <button type="button" className="btn-ghost" onClick={() => setAddServerTarget(null)}>
                Annuler
              </button>
              <button
                type="submit"
                className="btn-primary flex items-center gap-2"
                disabled={!serverForm.fqdn.trim() || addServerMutation.isPending}
              >
                {addServerMutation.isPending && <Spinner className="w-4 h-4" />}
                Ajouter
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}

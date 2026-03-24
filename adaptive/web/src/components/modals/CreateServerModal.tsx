import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Cpu } from 'lucide-react'
import { serversApi } from '../../api/servers'
import { vmTemplatesApi } from '../../api/vm-templates'
import { Modal } from '../Modal'
import { Spinner } from '../Spinner'
import type { Domain } from '../../types'

interface Props {
  projectId: number
  domains: Domain[]
  onSuccess: () => void
  onClose: () => void
}

export function CreateServerModal({ projectId, domains, onSuccess, onClose }: Props) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState({
    fqdn: '',
    is_dc: false,
    ip: '',
    gtw: '',
    dns: '',
    domain_id: domains[0]?.id.toString() ?? '',
    vm_template_id: '',
  })

  const { data: vmTemplates } = useQuery({
    queryKey: ['vm-templates'],
    queryFn: () => vmTemplatesApi.list(),
  })

  const mutation = useMutation({
    mutationFn: () =>
      serversApi.create(Number(form.domain_id), {
        fqdn: form.fqdn.trim(),
        is_dc: form.is_dc,
        ip: form.ip || undefined,
        gtw: form.gtw || undefined,
        dns: form.dns || undefined,
        vm_template_id: form.vm_template_id ? Number(form.vm_template_id) : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      onSuccess()
    },
  })

  return (
    <Modal title="Nouveau serveur" onClose={onClose}>
      <form
        onSubmit={(e) => {
          e.preventDefault()
          if (form.fqdn.trim() && form.domain_id) mutation.mutate()
        }}
        className="space-y-3"
      >
        <div>
          <label className="block text-sm text-slate-400 mb-1.5">Domaine parent</label>
          <select
            className="input"
            value={form.domain_id}
            onChange={(e) => setForm({ ...form, domain_id: e.target.value })}
          >
            {domains.map((d) => (
              <option key={d.id} value={d.id}>
                {d.fqdn}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-400 mb-1.5">FQDN</label>
          <input
            className="input"
            placeholder="ex: dc01.sub.corp.local"
            value={form.fqdn}
            onChange={(e) => setForm({ ...form, fqdn: e.target.value })}
            autoFocus
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm text-slate-400 mb-1.5">IP</label>
            <input
              className="input"
              placeholder="192.168.x.x"
              value={form.ip}
              onChange={(e) => setForm({ ...form, ip: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1.5">Passerelle</label>
            <input
              className="input"
              placeholder="192.168.x.1"
              value={form.gtw}
              onChange={(e) => setForm({ ...form, gtw: e.target.value })}
            />
          </div>
        </div>
        <div>
          <label className="block text-sm text-slate-400 mb-1.5">DNS</label>
          <input
            className="input"
            placeholder="192.168.x.x"
            value={form.dns}
            onChange={(e) => setForm({ ...form, dns: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-sm text-slate-400 mb-1.5">Template VM</label>
          <select
            className="input"
            value={form.vm_template_id}
            onChange={(e) => setForm({ ...form, vm_template_id: e.target.value })}
          >
            <option value="">— Aucun —</option>
            {vmTemplates?.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name} (VM #{t.vm_id})
              </option>
            ))}
          </select>
        </div>
        <label className="flex items-center gap-2 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={form.is_dc}
            onChange={(e) => setForm({ ...form, is_dc: e.target.checked })}
            className="rounded"
          />
          <span className="flex items-center gap-1.5 text-sm text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-success-400" /> Domain Controller
          </span>
        </label>
        <div className="flex gap-2 justify-end pt-1">
          <button type="button" className="btn-ghost" onClick={onClose}>
            Annuler
          </button>
          <button
            type="submit"
            className="btn-primary flex items-center gap-2"
            disabled={!form.fqdn.trim() || !form.domain_id || mutation.isPending}
          >
            {mutation.isPending && <Spinner className="w-4 h-4" />}
            Ajouter
          </button>
        </div>
      </form>
    </Modal>
  )
}

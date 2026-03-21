import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { domainsApi } from '../../api/domains'
import { Modal } from '../Modal'
import { Spinner } from '../Spinner'
import type { Forest } from '../../types'

interface Props {
  projectId: number
  forests: Forest[]
  onSuccess: () => void
  onClose: () => void
}

export function CreateDomainModal({ projectId, forests, onSuccess, onClose }: Props) {
  const queryClient = useQueryClient()
  const [fqdn, setFqdn] = useState('')
  const [forestId, setForestId] = useState(forests[0]?.id.toString() ?? '')

  const mutation = useMutation({
    mutationFn: () => domainsApi.create(Number(forestId), fqdn.trim()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      onSuccess()
    },
  })

  return (
    <Modal title="Nouveau domaine" onClose={onClose}>
      <form
        onSubmit={(e) => {
          e.preventDefault()
          if (fqdn.trim() && forestId) mutation.mutate()
        }}
        className="space-y-4"
      >
        <div>
          <label className="block text-sm text-slate-400 mb-1.5">Forêt parente</label>
          <select
            className="input"
            value={forestId}
            onChange={(e) => setForestId(e.target.value)}
          >
            {forests.map((f) => (
              <option key={f.id} value={f.id}>
                {f.fqdn}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-400 mb-1.5">FQDN du domaine</label>
          <input
            className="input"
            placeholder="ex: sub.corp.local"
            value={fqdn}
            onChange={(e) => setFqdn(e.target.value)}
            autoFocus
          />
        </div>
        <div className="flex gap-2 justify-end">
          <button type="button" className="btn-ghost" onClick={onClose}>
            Annuler
          </button>
          <button
            type="submit"
            className="btn-primary flex items-center gap-2"
            disabled={!fqdn.trim() || !forestId || mutation.isPending}
          >
            {mutation.isPending && <Spinner className="w-4 h-4" />}
            Ajouter
          </button>
        </div>
      </form>
    </Modal>
  )
}

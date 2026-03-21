import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { forestsApi } from '../../api/forests'
import { Modal } from '../Modal'
import { Spinner } from '../Spinner'

interface Props {
  projectId: number
  onSuccess: () => void
  onClose: () => void
}

export function CreateForestModal({ projectId, onSuccess, onClose }: Props) {
  const queryClient = useQueryClient()
  const [fqdn, setFqdn] = useState('')

  const mutation = useMutation({
    mutationFn: () => forestsApi.create(projectId, fqdn.trim()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      onSuccess()
    },
  })

  return (
    <Modal title="Nouvelle forêt" onClose={onClose}>
      <form
        onSubmit={(e) => {
          e.preventDefault()
          if (fqdn.trim()) mutation.mutate()
        }}
        className="space-y-4"
      >
        <div>
          <label className="block text-sm text-slate-400 mb-1.5">FQDN de la forêt</label>
          <input
            className="input"
            placeholder="ex: corp.local"
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
            disabled={!fqdn.trim() || mutation.isPending}
          >
            {mutation.isPending && <Spinner className="w-4 h-4" />}
            Ajouter
          </button>
        </div>
      </form>
    </Modal>
  )
}

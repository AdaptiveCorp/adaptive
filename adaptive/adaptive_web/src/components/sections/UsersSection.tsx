import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { UserRound, Plus } from 'lucide-react'
import { usersApi } from '../../api/users'
import { Modal } from '../Modal'
import { Spinner } from '../Spinner'
import type { Domain } from '../../types'

interface Props {
  projectId: number
  domains: Domain[]
}

export function UsersSection({ projectId, domains }: Props) {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({
    username: '',
    password: '',
    domain_id: '',
  })

  // Collect all users across all domains
  const userQueries = useQuery({
    queryKey: ['users', projectId],
    queryFn: async () => {
      const results = await Promise.all(
        domains.map((d) => usersApi.list({ domain_id: d.id }))
      )
      return results.flat()
    },
    enabled: domains.length > 0,
  })

  const addMutation = useMutation({
    mutationFn: () =>
      usersApi.create({
        username: form.username.trim(),
        password: form.password,
        domain_id: form.domain_id ? Number(form.domain_id) : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', projectId] })
      setOpen(false)
      setForm({ username: '', password: '', domain_id: '' })
    },
  })

  const users = userQueries.data ?? []

  return (
    <div className="card space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Utilisateurs AD
        </h2>
        <button
          className="btn-ghost text-xs flex items-center gap-1"
          onClick={() => setOpen(true)}
          disabled={domains.length === 0}
          title={domains.length === 0 ? 'Créez d\'abord un domaine' : undefined}
        >
          <Plus className="w-3.5 h-3.5" /> Utilisateur
        </button>
      </div>

      {userQueries.isLoading ? (
        <div className="flex justify-center py-6">
          <Spinner className="w-5 h-5 text-brand-400" />
        </div>
      ) : users.length === 0 ? (
        <p className="text-slate-500 text-sm text-center py-4">
          {domains.length === 0
            ? 'Créez un domaine avant d\'ajouter des utilisateurs.'
            : 'Aucun utilisateur — ajoutez-en pour configurer votre lab.'}
        </p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {users.map((user) => {
            const domain = domains.find((d) => d.id === user.domain_id)
            return (
              <div
                key={user.id}
                className="flex items-center gap-2 bg-dark-700 rounded-lg px-3 py-2"
              >
                <UserRound className="w-4 h-4 text-slate-400 shrink-0" />
                <div className="min-w-0">
                  <p className="text-sm text-slate-200 font-mono truncate">{user.username}</p>
                  {domain && (
                    <p className="text-xs text-slate-500 truncate">{domain.fqdn}</p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {open && (
        <Modal title="Nouvel utilisateur AD" onClose={() => setOpen(false)}>
          <form
            onSubmit={(e) => {
              e.preventDefault()
              addMutation.mutate()
            }}
            className="space-y-3"
          >
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">Nom d'utilisateur</label>
              <input
                className="input"
                placeholder="ex: jdoe"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                autoFocus
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">Mot de passe</label>
              <input
                className="input"
                type="password"
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1.5">Domaine</label>
              <select
                className="input"
                value={form.domain_id}
                onChange={(e) => setForm({ ...form, domain_id: e.target.value })}
              >
                <option value="">-- Sélectionner --</option>
                {domains.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.fqdn}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-2 justify-end pt-1">
              <button type="button" className="btn-ghost" onClick={() => setOpen(false)}>
                Annuler
              </button>
              <button
                type="submit"
                className="btn-primary flex items-center gap-2"
                disabled={
                  !form.username.trim() ||
                  !form.password ||
                  !form.domain_id ||
                  addMutation.isPending
                }
              >
                {addMutation.isPending && <Spinner className="w-4 h-4" />}
                Ajouter
              </button>
            </div>
            {addMutation.isError && (
              <p className="text-danger-400 text-sm">Erreur lors de la création.</p>
            )}
          </form>
        </Modal>
      )}
    </div>
  )
}

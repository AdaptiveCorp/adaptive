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
    firstname: '',
    lastname: '',
    password: '',
    domain_id: '',
  })

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
        firstname: form.firstname.trim(),
        lastname: form.lastname.trim(),
        password: form.password,
        domain_id: form.domain_id ? Number(form.domain_id) : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', projectId] })
      setOpen(false)
      setForm({ firstname: '', lastname: '', password: '', domain_id: '' })
    },
  })

  const users = userQueries.data ?? []

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
          Utilisateurs AD
        </span>
        <button
          className="btn-ghost"
          style={{ padding: '5px 12px', fontSize: 12 }}
          onClick={() => setOpen(true)}
          disabled={domains.length === 0}
          title={domains.length === 0 ? "Créez d'abord un domaine" : undefined}
        >
          <Plus className="w-3.5 h-3.5" /> Utilisateur
        </button>
      </div>

      {userQueries.isLoading ? (
        <div className="flex justify-center py-6">
          <Spinner className="w-5 h-5 text-brand-400" />
        </div>
      ) : users.length === 0 ? (
        <p style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: '#475569', textAlign: 'center', padding: '16px 0' }}>
          {domains.length === 0
            ? "Créez un domaine avant d'ajouter des utilisateurs."
            : 'Aucun utilisateur — ajoutez-en pour configurer votre lab.'}
        </p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {users.map((user) => {
            const domain = domains.find((d) => d.id === user.domain_id)
            return (
              <div
                key={user.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  background: 'rgba(15, 32, 52, 0.6)',
                  border: '1px solid rgba(22, 40, 64, 0.7)',
                  borderRadius: 7,
                  padding: '10px 12px',
                }}
              >
                <UserRound style={{ width: 14, height: 14, color: '#64748B', flexShrink: 0 }} />
                <div style={{ minWidth: 0 }}>
                  <p style={{ fontFamily: "'Fira Code', monospace", fontSize: 13, color: '#CBD5E1', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginBottom: 1 }}>
                    {user.username}
                  </p>
                  {domain && (
                    <p style={{ fontSize: 11, color: '#64748B', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontFamily: "'Fira Code', monospace" }}>
                      {domain.fqdn}
                    </p>
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
            onSubmit={(e) => { e.preventDefault(); addMutation.mutate() }}
            className="space-y-3"
          >
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label>Prénom</label>
                <input className="input" placeholder="ex: John" value={form.firstname}
                  onChange={(e) => setForm({ ...form, firstname: e.target.value })} autoFocus />
              </div>
              <div>
                <label>Nom</label>
                <input className="input" placeholder="ex: Doe" value={form.lastname}
                  onChange={(e) => setForm({ ...form, lastname: e.target.value })} />
              </div>
            </div>
            <div>
              <label>Mot de passe</label>
              <input className="input" type="password" placeholder="••••••••" value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })} />
            </div>
            <div>
              <label>Domaine</label>
              <select className="input" value={form.domain_id}
                onChange={(e) => setForm({ ...form, domain_id: e.target.value })}>
                <option value="">— Sélectionner —</option>
                {domains.map((d) => (
                  <option key={d.id} value={d.id}>{d.fqdn}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-2 justify-end pt-1">
              <button type="button" className="btn-ghost" onClick={() => setOpen(false)}>Annuler</button>
              <button
                type="submit"
                className="btn-primary"
                disabled={!form.firstname.trim() || !form.lastname.trim() || !form.password || !form.domain_id || addMutation.isPending}
              >
                {addMutation.isPending && <Spinner className="w-4 h-4" />}
                Ajouter
              </button>
            </div>
            {addMutation.isError && (
              <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace" }}>
                Erreur lors de la création.
              </p>
            )}
          </form>
        </Modal>
      )}
    </div>
  )
}

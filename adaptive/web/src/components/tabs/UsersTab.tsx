import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Users, Plus } from 'lucide-react'
import { usersApi } from '../../api/users'
import { Modal } from '../Modal'
import { Spinner } from '../Spinner'
import type { Domain } from '../../types'

interface Props {
  projectId: number
  domains: Domain[]
}

export function UsersTab({ projectId, domains }: Props) {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({
    firstname: '',
    lastname: '',
    username: '',
    password: '',
    domain_id: '',
  })

  const { data: users, isLoading } = useQuery({
    queryKey: ['users', projectId],
    queryFn: async () => {
      const results = await Promise.all(domains.map((d) => usersApi.list({ domain_id: d.id })))
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
        username: form.username.trim() || undefined,
        domain_id: form.domain_id ? Number(form.domain_id) : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', projectId] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      setOpen(false)
      setForm({ firstname: '', lastname: '', username: '', password: '', domain_id: '' })
    },
  })

  const allUsers = users ?? []

  return (
    <div className="space-y-4">
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
          <Plus className="w-3.5 h-3.5" /> Ajouter
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner className="w-5 h-5 text-brand-400" />
        </div>
      ) : allUsers.length === 0 ? (
        <div style={{
          background: 'rgba(10, 23, 40, 0.6)',
          border: '1px dashed rgba(22, 40, 64, 0.8)',
          borderRadius: 10,
          padding: '48px 24px',
          textAlign: 'center',
        }}>
          <Users style={{ width: 32, height: 32, color: '#475569', margin: '0 auto 12px' }} />
          <p style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: '#475569' }}>
            {domains.length === 0
              ? "Créez un domaine avant d'ajouter des utilisateurs."
              : 'Aucun utilisateur — ajoutez-en pour configurer votre lab.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {allUsers.map((user) => {
            const domain = domains.find((d) => d.id === user.domain_id)
            const initials = user.username?.slice(0, 2).toUpperCase() ?? '??'
            return (
              <div key={user.id} style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                background: 'rgba(10, 23, 40, 0.85)',
                border: '1px solid rgba(22, 40, 64, 0.8)',
                borderRadius: 8,
                padding: '12px 14px',
              }}>
                <div style={{
                  width: 36,
                  height: 36,
                  borderRadius: 8,
                  background: 'rgba(251, 191, 36, 0.1)',
                  border: '1px solid rgba(251, 191, 36, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontWeight: 600,
                  fontSize: 13,
                  color: '#FBBF24',
                }}>
                  {initials}
                </div>
                <div style={{ minWidth: 0 }}>
                  <p style={{ fontFamily: "'Fira Code', monospace", fontSize: 13, color: '#CBD5E1', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginBottom: 2 }}>
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
              <label>Nom d'utilisateur <span style={{ color: '#475569', textTransform: 'none', fontSize: 10 }}>(optionnel)</span></label>
              <input className="input" placeholder="ex: jdoe" value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })} />
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

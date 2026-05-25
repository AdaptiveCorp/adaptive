import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Users, Plus, Trash2 } from 'lucide-react'
import { usersApi } from '../../api/users'
import { groupsApi } from '../../api/groups'
import { Modal } from '../Modal'
import { Spinner } from '../Spinner'
import type { Domain, Group, User } from '../../types'

interface Props {
  projectId: number
  domains: Domain[]
}

export function UsersTab({ projectId, domains }: Props) {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [delTarget, setDelTarget] = useState<User | null>(null)
  const [editUser, setEditUser] = useState<User | null>(null)
  const [editGroupIds, setEditGroupIds] = useState<number[]>([])
  const [form, setForm] = useState({
    firstname: '',
    lastname: '',
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

  const { data: allGroups = [] } = useQuery<Group[]>({
    queryKey: ['groups'],
    queryFn: () => groupsApi.list(),
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
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      setOpen(false)
      setForm({ firstname: '', lastname: '', password: '', domain_id: '' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => usersApi.delete(id),
    onSuccess: (_, id) => {
      queryClient.setQueryData<User[]>(['users', projectId], old =>
        (old ?? []).filter(u => u.id !== id)
      )
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      setDelTarget(null)
    },
  })

  const editGroupsMut = useMutation({
    mutationFn: async ({ user, selectedIds }: { user: User; selectedIds: number[] }) => {
      const initialIds = allGroups.filter(g => g.user_ids.includes(user.id)).map(g => g.id)
      const toAdd    = selectedIds.filter(id => !initialIds.includes(id))
      const toRemove = initialIds.filter(id => !selectedIds.includes(id))
      await Promise.all([
        ...toAdd.map(gid => groupsApi.addMembers(gid, [user.id])),
        ...toRemove.map(gid => groupsApi.removeMember(gid, user.id)),
      ])
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
      setEditUser(null)
    },
  })

  function openUserEdit(u: User) {
    const currentGroupIds = allGroups.filter(g => g.user_ids.includes(u.id)).map(g => g.id)
    setEditGroupIds(currentGroupIds)
    setEditUser(u)
  }

  function toggleGroup(id: number) {
    setEditGroupIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  const allUsers = users ?? []

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 10, fontWeight: 600,
          color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em',
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
          background: 'var(--bg-card)', border: '1px dashed var(--border-input)',
          borderRadius: 10, padding: '48px 24px', textAlign: 'center',
        }}>
          <Users style={{ width: 32, height: 32, color: 'var(--text-dim)', margin: '0 auto 12px' }} />
          <p style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: 'var(--text-dim)' }}>
            {domains.length === 0
              ? "Créez un domaine avant d'ajouter des utilisateurs."
              : 'Aucun utilisateur — ajoutez-en pour configurer votre lab.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {allUsers.map((user) => {
            const domain  = domains.find((d) => d.id === user.domain_id)
            const initials = user.username?.slice(0, 2).toUpperCase() ?? '??'
            const groupCount = allGroups.filter(g => g.user_ids.includes(user.id)).length
            return (
              <div
                key={user.id}
                onClick={() => openUserEdit(user)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  background: 'var(--bg-card)', border: '1px solid var(--border-card)',
                  borderRadius: 8, padding: '12px 14px',
                  cursor: 'pointer', transition: 'border-color 0.15s',
                }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--brand-400)' }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--border-card)' }}
              >
                <div style={{
                  width: 36, height: 36, borderRadius: 8,
                  background: 'rgba(251, 191, 36, 0.1)', border: '1px solid rgba(251, 191, 36, 0.2)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                  fontFamily: "'IBM Plex Mono', monospace", fontWeight: 600, fontSize: 13, color: '#FBBF24',
                }}>
                  {initials}
                </div>
                <div style={{ minWidth: 0, flex: 1 }}>
                  <p style={{
                    fontFamily: "'Fira Code', monospace", fontSize: 13, color: 'var(--text-bright)',
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginBottom: 2,
                  }}>
                    {user.username}
                  </p>
                  <p style={{
                    fontSize: 11, color: 'var(--text-dim)',
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                    fontFamily: "'Fira Code', monospace",
                  }}>
                    {domain?.fqdn ?? ''}
                    {groupCount > 0 && (
                      <span style={{ marginLeft: 6, color: 'var(--text-muted)' }}>
                        · {groupCount} groupe{groupCount > 1 ? 's' : ''}
                      </span>
                    )}
                  </p>
                </div>
                <button
                  onClick={e => { e.stopPropagation(); setDelTarget(user) }}
                  title="Supprimer"
                  className="row-del"
                  style={{ flexShrink: 0 }}
                >
                  <Trash2 style={{ width: 13, height: 13 }} />
                </button>
              </div>
            )
          })}
        </div>
      )}

      {/* Create modal */}
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
                type="submit" className="btn-primary"
                disabled={!form.firstname.trim() || !form.lastname.trim() || !form.password || !form.domain_id || addMutation.isPending}
              >
                {addMutation.isPending && <Spinner className="w-4 h-4" />}
                Ajouter
              </button>
            </div>
            {addMutation.isError && (
              <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace", marginTop: 8 }}>
                Erreur lors de la création.
              </p>
            )}
          </form>
        </Modal>
      )}

      {/* Edit user groups modal */}
      {editUser && (() => {
        const domainGroups = allGroups.filter(g => g.domain_id === editUser.domain_id)
        return (
          <Modal
            title={`Groupes — ${editUser.username}`}
            onClose={() => setEditUser(null)}
          >
            {domainGroups.length === 0 ? (
              <p style={{ fontSize: 13, color: 'var(--text-dim)', fontFamily: "'IBM Plex Mono', monospace", textAlign: 'center', padding: '20px 0' }}>
                Aucun groupe dans ce domaine.
              </p>
            ) : (
              <div style={{
                background: 'var(--bg-input)', border: '1px solid var(--border-input)',
                borderRadius: 7, maxHeight: 260, overflowY: 'auto', padding: '6px 0', marginBottom: 16,
              }}>
                {domainGroups.map(g => (
                  <label key={g.id} style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '7px 14px', cursor: 'pointer',
                  }}>
                    <input
                      type="checkbox"
                      checked={editGroupIds.includes(g.id)}
                      onChange={() => toggleGroup(g.id)}
                    />
                    <div style={{ minWidth: 0 }}>
                      <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 13, color: 'var(--text-bright)' }}>
                        {g.name}
                      </span>
                      {g.description && (
                        <span style={{ fontSize: 11, color: 'var(--text-dim)', marginLeft: 8 }}>
                          {g.description}
                        </span>
                      )}
                    </div>
                    <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--text-muted)', fontFamily: "'IBM Plex Mono', monospace", flexShrink: 0 }}>
                      {g.user_ids.length} membre{g.user_ids.length !== 1 ? 's' : ''}
                    </span>
                  </label>
                ))}
              </div>
            )}
            <div className="flex gap-2 justify-end">
              <button className="btn-ghost" onClick={() => setEditUser(null)}>Annuler</button>
              <button
                className="btn-primary"
                disabled={editGroupsMut.isPending || domainGroups.length === 0}
                onClick={() => editGroupsMut.mutate({ user: editUser, selectedIds: editGroupIds })}
              >
                {editGroupsMut.isPending && <Spinner className="w-3.5 h-3.5" />}
                Enregistrer
              </button>
            </div>
            {editGroupsMut.isError && (
              <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace", marginTop: 12 }}>
                Erreur lors de la mise à jour des groupes.
              </p>
            )}
          </Modal>
        )
      })()}

      {/* Delete confirm */}
      {delTarget && (
        <Modal title="Supprimer l'utilisateur" onClose={() => setDelTarget(null)}>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 8, lineHeight: 1.6 }}>
            Supprimer{' '}
            <span style={{ fontFamily: "'Fira Code', monospace", color: 'var(--text-bright)', fontWeight: 500 }}>
              {delTarget.username}
            </span>{' '}?
          </p>
          <p style={{ fontSize: 12, color: 'var(--text-dim)', marginBottom: 20, lineHeight: 1.5 }}>
            La suppression sera effective au prochain déploiement.
          </p>
          <div className="flex gap-2 justify-end">
            <button className="btn-ghost" onClick={() => setDelTarget(null)}>Annuler</button>
            <button
              className="btn-danger"
              disabled={deleteMutation.isPending}
              onClick={() => deleteMutation.mutate(delTarget.id)}
            >
              {deleteMutation.isPending && <Spinner className="w-3.5 h-3.5" />}
              Supprimer
            </button>
          </div>
          {deleteMutation.isError && (
            <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace", marginTop: 12 }}>
              Impossible de supprimer cet utilisateur.
            </p>
          )}
        </Modal>
      )}
    </div>
  )
}

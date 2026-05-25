import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, UsersRound } from 'lucide-react'
import { groupsApi } from '../../api/groups'
import { usersApi }  from '../../api/users'
import { Modal }   from '../Modal'
import { Spinner } from '../Spinner'
import type { Domain, Group, User } from '../../types'

interface Props {
  projectId: number
  domains: Domain[]
}

export function GroupsTab({ projectId, domains }: Props) {
  const queryClient = useQueryClient()
  const domainIds = domains.map(d => d.id)

  const [showCreate, setShowCreate] = useState(false)
  const [delTarget, setDelTarget]   = useState<Group | null>(null)
  const [editGroup, setEditGroup]   = useState<Group | null>(null)
  const [editMemberIds, setEditMemberIds] = useState<number[]>([])

  const [form, setForm] = useState({
    name: '',
    description: '',
    domain_id: domains[0]?.id ?? 0,
  })
  const [selectedUserIds, setSelectedUserIds] = useState<number[]>([])

  const { data: allGroups, isLoading } = useQuery({
    queryKey: ['groups'],
    queryFn: () => groupsApi.list(),
  })
  const groups = (allGroups ?? []).filter(g =>
    g.domain_id !== null && domainIds.includes(g.domain_id)
  )

  const { data: domainUsers } = useQuery({
    queryKey: ['users', projectId, form.domain_id],
    queryFn: () => usersApi.list({ domain_id: form.domain_id }),
    enabled: !!form.domain_id,
  })

  const { data: editGroupUsers = [] } = useQuery<User[]>({
    queryKey: ['users', projectId, editGroup?.domain_id],
    queryFn: () => usersApi.list({ domain_id: editGroup!.domain_id! }),
    enabled: !!editGroup?.domain_id,
  })

  const createMut = useMutation({
    mutationFn: () => groupsApi.create({
      name: form.name.trim(),
      description: form.description.trim() || undefined,
      domain_id: form.domain_id || undefined,
      user_ids: selectedUserIds,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      setShowCreate(false)
      resetForm()
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => groupsApi.delete(id),
    onSuccess: (_, id) => {
      queryClient.setQueryData<Group[]>(['groups'], old =>
        (old ?? []).filter(g => g.id !== id)
      )
      queryClient.invalidateQueries({ queryKey: ['project', projectId] })
      setDelTarget(null)
    },
  })

  const editMembersMut = useMutation({
    mutationFn: async ({ group, selectedIds }: { group: Group; selectedIds: number[] }) => {
      const toAdd    = selectedIds.filter(id => !group.user_ids.includes(id))
      const toRemove = group.user_ids.filter(id => !selectedIds.includes(id))
      await Promise.all([
        ...(toAdd.length ? [groupsApi.addMembers(group.id, toAdd)] : []),
        ...toRemove.map(uid => groupsApi.removeMember(group.id, uid)),
      ])
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
      setEditGroup(null)
    },
  })

  function resetForm() {
    setForm({ name: '', description: '', domain_id: domains[0]?.id ?? 0 })
    setSelectedUserIds([])
  }

  function toggleUser(id: number) {
    setSelectedUserIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  function toggleMember(id: number) {
    setEditMemberIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  function openGroupEdit(g: Group) {
    setEditMemberIds([...g.user_ids])
    setEditGroup(g)
  }

  const domainLabel = (id: number) =>
    domains.find(d => d.id === id)?.fqdn ?? `#${id}`

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span style={{
          fontFamily: "'IBM Plex Mono', monospace",
          fontSize: 10, fontWeight: 600,
          color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em',
        }}>
          Groupes AD
        </span>
        <button
          className="btn-ghost"
          style={{ padding: '5px 12px', fontSize: 12 }}
          onClick={() => { resetForm(); setShowCreate(true) }}
          disabled={domains.length === 0}
          title={domains.length === 0 ? "Créez d'abord un domaine" : undefined}
        >
          <Plus className="w-3.5 h-3.5" /> Nouveau groupe
        </button>
      </div>

      {/* List */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner className="w-5 h-5 text-brand-400" />
        </div>
      ) : groups.length === 0 ? (
        <div style={{
          background: 'var(--bg-card)', border: '1px dashed var(--border-input)',
          borderRadius: 10, padding: '48px 24px', textAlign: 'center',
        }}>
          <UsersRound style={{ width: 32, height: 32, color: 'var(--text-dim)', margin: '0 auto 12px' }} />
          <p style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: 'var(--text-dim)' }}>
            {domains.length === 0
              ? "Créez un domaine avant d'ajouter des groupes."
              : 'Aucun groupe — créez-en pour configurer votre lab AD.'}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {groups.map((g, i) => (
            <div
              key={g.id}
              className="animate-enter project-row"
              style={{ animationDelay: `${i * 40}ms`, cursor: 'pointer' }}
              onClick={() => openGroupEdit(g)}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{
                  fontFamily: "'IBM Plex Mono', monospace", fontWeight: 600,
                  fontSize: 15, color: 'var(--text-bright)', letterSpacing: '-0.02em',
                  marginBottom: 3, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                }}>
                  {g.name}
                </p>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                  {g.domain_id && (
                    <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 11, color: 'var(--text-muted)' }}>
                      {domainLabel(g.domain_id)}
                    </span>
                  )}
                  <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>
                    {g.user_ids.length} utilisateur{g.user_ids.length !== 1 ? 's' : ''}
                  </span>
                  {g.description && (
                    <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>
                      — {g.description}
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={e => { e.stopPropagation(); setDelTarget(g) }}
                title="Supprimer" className="row-del"
              >
                <Trash2 style={{ width: 13, height: 13 }} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Create modal */}
      {showCreate && (
        <Modal title="Nouveau groupe AD" onClose={() => setShowCreate(false)}>
          <form
            onSubmit={e => { e.preventDefault(); if (form.name.trim()) createMut.mutate() }}
            className="space-y-4"
          >
            <div>
              <label>Nom</label>
              <input
                className="input" placeholder="ex: Domain Admins"
                value={form.name} autoFocus
                onChange={e => setForm({ ...form, name: e.target.value })}
              />
            </div>
            <div>
              <label>Description <span style={{ color: 'var(--text-dim)', textTransform: 'none', fontSize: 10 }}>(optionnel)</span></label>
              <input
                className="input" placeholder="ex: Administrateurs du domaine"
                value={form.description}
                onChange={e => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <div>
              <label>Domaine</label>
              <select
                className="input"
                value={form.domain_id}
                onChange={e => {
                  setForm({ ...form, domain_id: Number(e.target.value) })
                  setSelectedUserIds([])
                }}
              >
                {domains.map(d => (
                  <option key={d.id} value={d.id}>{d.fqdn}</option>
                ))}
              </select>
            </div>
            {domainUsers && domainUsers.length > 0 && (
              <div>
                <label>Membres <span style={{ color: 'var(--text-dim)', textTransform: 'none', fontSize: 10 }}>(optionnel)</span></label>
                <div style={{
                  background: 'var(--bg-input)', border: '1px solid var(--border-input)',
                  borderRadius: 7, maxHeight: 140, overflowY: 'auto', padding: '6px 0',
                }}>
                  {domainUsers.map((u: User) => (
                    <label key={u.id} style={{
                      display: 'flex', alignItems: 'center', gap: 8,
                      padding: '5px 12px', cursor: 'pointer',
                    }}>
                      <input
                        type="checkbox"
                        checked={selectedUserIds.includes(u.id)}
                        onChange={() => toggleUser(u.id)}
                      />
                      <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 12, color: 'var(--text-bright)' }}>
                        {u.username}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            )}
            <div className="flex gap-2 justify-end">
              <button type="button" className="btn-ghost" onClick={() => setShowCreate(false)}>Annuler</button>
              <button
                type="submit" className="btn-primary"
                disabled={!form.name.trim() || !form.domain_id || createMut.isPending}
              >
                {createMut.isPending && <Spinner className="w-3.5 h-3.5" />}
                Créer
              </button>
            </div>
            {createMut.isError && (
              <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace" }}>
                Erreur lors de la création (nom déjà utilisé ?).
              </p>
            )}
          </form>
        </Modal>
      )}

      {/* Edit members modal */}
      {editGroup && (
        <Modal
          title={`Membres — ${editGroup.name}`}
          onClose={() => setEditGroup(null)}
        >
          {editGroupUsers.length === 0 ? (
            <p style={{ fontSize: 13, color: 'var(--text-dim)', fontFamily: "'IBM Plex Mono', monospace", textAlign: 'center', padding: '20px 0' }}>
              Aucun utilisateur dans ce domaine.
            </p>
          ) : (
            <div style={{
              background: 'var(--bg-input)', border: '1px solid var(--border-input)',
              borderRadius: 7, maxHeight: 260, overflowY: 'auto', padding: '6px 0', marginBottom: 16,
            }}>
              {editGroupUsers.map(u => (
                <label key={u.id} style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  padding: '7px 14px', cursor: 'pointer',
                }}>
                  <input
                    type="checkbox"
                    checked={editMemberIds.includes(u.id)}
                    onChange={() => toggleMember(u.id)}
                  />
                  <span style={{ fontFamily: "'Fira Code', monospace", fontSize: 13, color: 'var(--text-bright)' }}>
                    {u.username}
                  </span>
                </label>
              ))}
            </div>
          )}
          <div className="flex gap-2 justify-end">
            <button className="btn-ghost" onClick={() => setEditGroup(null)}>Annuler</button>
            <button
              className="btn-primary"
              disabled={editMembersMut.isPending || editGroupUsers.length === 0}
              onClick={() => editMembersMut.mutate({ group: editGroup, selectedIds: editMemberIds })}
            >
              {editMembersMut.isPending && <Spinner className="w-3.5 h-3.5" />}
              Enregistrer
            </button>
          </div>
          {editMembersMut.isError && (
            <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace", marginTop: 12 }}>
              Erreur lors de la mise à jour des membres.
            </p>
          )}
        </Modal>
      )}

      {/* Delete confirm */}
      {delTarget && (
        <Modal title="Supprimer le groupe" onClose={() => setDelTarget(null)}>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 8, lineHeight: 1.6 }}>
            Supprimer{' '}
            <span style={{ fontFamily: "'Fira Code', monospace", color: 'var(--text-bright)', fontWeight: 500 }}>
              {delTarget.name}
            </span>{' '}?
          </p>
          <p style={{ fontSize: 12, color: 'var(--text-dim)', marginBottom: 20, lineHeight: 1.5 }}>
            La suppression sera effective au prochain déploiement.
          </p>
          <div className="flex gap-2 justify-end">
            <button className="btn-ghost" onClick={() => setDelTarget(null)}>Annuler</button>
            <button
              className="btn-danger"
              disabled={deleteMut.isPending}
              onClick={() => deleteMut.mutate(delTarget.id)}
            >
              {deleteMut.isPending && <Spinner className="w-3.5 h-3.5" />}
              Supprimer
            </button>
          </div>
          {deleteMut.isError && (
            <p style={{ fontSize: 12, color: '#FB7185', fontFamily: "'IBM Plex Mono', monospace", marginTop: 12 }}>
              Impossible de supprimer ce groupe.
            </p>
          )}
        </Modal>
      )}
    </div>
  )
}

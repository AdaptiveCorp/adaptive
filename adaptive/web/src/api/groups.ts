import client from './client'
import type { Group } from '../types'

interface GroupCreatePayload {
  name: string
  description?: string
  domain_id?: number
  server_id?: number
  user_ids?: number[]
}

export const groupsApi = {
  list: () =>
    client.get<Group[]>('/groups/').then(r => r.data),

  get: (id: number) =>
    client.get<Group>(`/groups/${id}`).then(r => r.data),

  create: (payload: GroupCreatePayload) =>
    client.post<Group>('/groups/', payload).then(r => r.data),

  addMembers: (groupId: number, userIds: number[]) =>
    client.post<Group>(`/groups/${groupId}/members`, { user_ids: userIds }).then(r => r.data),

  removeMember: (groupId: number, userId: number) =>
    client.delete<{ success: boolean }>(`/groups/${groupId}/${userId}`).then(r => r.data),

  delete: (id: number) =>
    client.delete<{ success: boolean }>(`/groups/${id}`).then(r => r.data),
}

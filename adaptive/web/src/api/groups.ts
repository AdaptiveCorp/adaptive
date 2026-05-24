import client from './client'
import type { Group } from '../types'

interface GroupCreatePayload {
  name: string
  description?: string
  domain_id?: number
  server_id?: number
  user_ids?: number[]
  member_group_ids?: number[]
}

export const groupsApi = {
  list: () =>
    client.get<Group[]>('/groups/').then(r => r.data),

  create: (payload: GroupCreatePayload) =>
    client.post<Group>('/groups/', payload).then(r => r.data),

  delete: (id: number) =>
    client.delete<{ success: boolean }>(`/groups/${id}`).then(r => r.data),
}

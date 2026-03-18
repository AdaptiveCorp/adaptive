import type { Forest } from '../types'
import client from './client'

export const forestsApi = {
  list: async (projectId: number): Promise<Forest[]> => {
    const res = await client.get<Forest[]>(`/projects/${projectId}/forests/`)
    return res.data
  },

  create: async (projectId: number, fqdn: string): Promise<Forest> => {
    const res = await client.post<Forest>(`/projects/${projectId}/forests/`, null, {
      params: { fqdn },
    })
    return res.data
  },
}

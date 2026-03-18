import type { Domain } from '../types'
import client from './client'

export const domainsApi = {
  list: async (forestId: number): Promise<Domain[]> => {
    const res = await client.get<Domain[]>(`/forests/${forestId}/domains/`)
    return res.data
  },

  create: async (forestId: number, fqdn: string): Promise<Domain> => {
    const res = await client.post<Domain>(`/forests/${forestId}/domains/`, null, {
      params: { fqdn },
    })
    return res.data
  },
}

import type { Server } from '../types'
import client from './client'

export interface CreateServerParams {
  fqdn: string
  is_dc?: boolean
  ip?: string
  gtw?: string
  dns?: string
}

export const serversApi = {
  list: async (domainId: number): Promise<Server[]> => {
    const res = await client.get<Server[]>(`/domains/${domainId}/servers/`)
    return res.data
  },

  create: async (domainId: number, params: CreateServerParams): Promise<Server> => {
    const res = await client.post<Server>(`/domains/${domainId}/servers/`, null, {
      params: { ...params },
    })
    return res.data
  },
}

import type { User } from '../types'
import client from './client'

export interface CreateUserParams {
  firstname: string
  lastname: string
  password: string
  domain_id?: number
  server_id?: number
}

export const usersApi = {
  list: async (params: { domain_id?: number; server_id?: number }): Promise<User[]> => {
    const res = await client.get<User[]>('/users/', { params })
    return res.data
  },

  create: async (params: CreateUserParams): Promise<User> => {
    const res = await client.post<User>('/users/', params)
    return res.data
  },

  delete: async (id: number): Promise<{ success: boolean }> => {
    const res = await client.delete<{ success: boolean }>(`/users/${id}`)
    return res.data
  },
}

import type { VmTemplate } from '../types'
import client from './client'

export const vmTemplatesApi = {
  list: async (): Promise<VmTemplate[]> => {
    const res = await client.get<VmTemplate[]>('/vm-templates/')
    return res.data
  },

  create: async (payload: {
    name: string
    vm_id: number
    description?: string
  }): Promise<VmTemplate> => {
    const res = await client.post<VmTemplate>('/vm-templates/', payload)
    return res.data
  },

  delete: async (id: number): Promise<void> => {
    await client.delete(`/vm-templates/${id}`)
  },
}

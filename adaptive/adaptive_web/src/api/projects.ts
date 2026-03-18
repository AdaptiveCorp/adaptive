import type { Project, ProjectDetail, DeployResult } from '../types'
import client from './client'

export const projectsApi = {
  list: async (): Promise<Project[]> => {
    const res = await client.get<Project[]>('/projects/')
    return res.data
  },

  get: async (id: number): Promise<ProjectDetail> => {
    const res = await client.get<ProjectDetail>(`/projects/${id}`)
    return res.data
  },

  create: async (name: string): Promise<Project> => {
    const res = await client.post<Project>('/projects/', null, { params: { name } })
    return res.data
  },

  delete: async (id: number): Promise<void> => {
    await client.delete(`/projects/${id}`)
  },

  deploy: async (id: number): Promise<DeployResult> => {
    const res = await client.post<DeployResult>(`/projects/${id}/deploy`)
    return res.data
  },
}

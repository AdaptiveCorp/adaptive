import type { Vulnerability, AppliedVulnerability } from '../types'
import client from './client'

export const vulnerabilitiesApi = {
  list: async (): Promise<Vulnerability[]> => {
    const res = await client.get<Vulnerability[]>('/vulnerabilities/')
    return res.data
  },

  listApplied: async (projectId: number): Promise<AppliedVulnerability[]> => {
    const res = await client.get<AppliedVulnerability[]>(
      `/vulnerabilities/projects/${projectId}`
    )
    return res.data
  },

  removeApplied: async (vulnId: number): Promise<void> => {
    await client.delete(`/vulnerabilities/${vulnId}`)
  },
}

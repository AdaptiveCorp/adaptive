// ---- Core entities ----

export interface Project {
  id: number
  name: string
  created_at: string
}

export interface ProjectDetail {
  project: Project
  forests: Forest[]
  domains: Domain[]
  servers: Server[]
  users: User[]
  vulnerabilities_count: number
}

export interface Forest {
  id: number
  fqdn: string
  project_id: number
}

export interface Domain {
  id: number
  fqdn: string
  forest_id: number
}

export interface Server {
  id: number
  fqdn: string
  is_dc: boolean
  ip: string | null
  gtw?: string | null
  dns?: string | null
  vm_id?: number | null
  domain_id: number | null
}

export interface User {
  id: number
  username: string
  domain_id: number | null
  server_id: number | null
}

export interface Vulnerability {
  id: number
  code: string
  name: string
  description: string | null
  category: string | null
}

export interface AppliedVulnerability {
  id: number
  vulnerability: { code: string; name: string }
  source_user_id: number | null
  user_id: number | null
  domain_id: number | null
  server_id: number | null
  forest_id: number | null
  params: string | null
  created_at: string
}

// ---- API response shapes ----

export interface DeployResult {
  project: string
  deployment_result: {
    success: boolean
    error?: string | null
    message?: string
  }
}

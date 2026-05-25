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
  vm_id: number | null
  domain_id: number
  vm_template_id?: number | null
  vm_template_name?: string | null
  status?: string | null
}

export interface User {
  id: number
  username: string
  domain_id: number | null
  server_id?: number | null
}

export interface Vulnerability {
  id: number
  code: string
  name: string
  description: string | null
  category: string | null
  required_params: string | null
}

export interface AppliedVulnerability {
  id: number
  template: { code: string; name: string }
  user_id: number | null
  domain_id: number | null
  server_id: number | null
  forest_id: number | null
  params: string | null
  status: string
  created_at: string
}

export interface Group {
  id: number
  name: string
  description: string | null
  domain_id: number | null
  server_id: number | null
  user_ids: number[]
}

export interface VmTemplate {
  id: number
  name: string
  vm_id: number
  description: string | null
}

// ---- API response shapes ----

export interface DeployResult {
  project_name: string
  success: boolean
  message: string | null
  error: string | null
  clone_results: { success: boolean; server_id: number; vm_id: number | null; error: string | null }[]
}

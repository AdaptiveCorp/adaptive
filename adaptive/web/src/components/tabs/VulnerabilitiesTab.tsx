import { VulnerabilitiesSection } from '../sections/VulnerabilitiesSection'
import type { Domain, User } from '../../types'

interface Props {
  projectId: number
  domains: Domain[]
  users: User[]
}

export function VulnerabilitiesTab({ projectId, domains, users }: Props) {
  return <VulnerabilitiesSection projectId={projectId} domains={domains} users={users} />
}

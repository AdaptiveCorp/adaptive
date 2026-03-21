import { VulnerabilitiesSection } from '../sections/VulnerabilitiesSection'

interface Props {
  projectId: number
}

export function VulnerabilitiesTab({ projectId }: Props) {
  return <VulnerabilitiesSection projectId={projectId} />
}

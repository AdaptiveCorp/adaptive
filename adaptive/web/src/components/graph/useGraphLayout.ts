import type { Forest, Domain, Server, User } from '../../types'

export interface GraphNode {
  id: string
  label: string
  type: 'forest' | 'domain' | 'server' | 'user'
  x: number
  y: number
  width: number
  height: number
  meta?: { is_dc?: boolean }
}

export interface GraphEdge {
  from: string
  to: string
}

const NODE_W   = 178
const NODE_H   = 58
const GAP_Y    = 14
const FOREST_GAP = 28
const PADDING  = 28
const COL_GAP  = 44

const COL_X = [0, 1, 2, 3].map(i => PADDING + i * (NODE_W + COL_GAP))

function colChildrenHeight(count: number): number {
  if (count === 0) return 0
  return count * NODE_H + (count - 1) * GAP_Y
}

function domainSubtreeHeight(domain: Domain, servers: Server[], users: User[]): number {
  const sCount = servers.filter(s => s.domain_id === domain.id).length
  const uRaw   = users.filter(u => u.domain_id === domain.id).length
  const uCount = uRaw > 10 ? 1 : uRaw
  return Math.max(colChildrenHeight(sCount), colChildrenHeight(uCount), NODE_H)
}

function forestSubtreeHeight(forest: Forest, domains: Domain[], servers: Server[], users: User[]): number {
  const fDomains = domains.filter(d => d.forest_id === forest.id)
  if (fDomains.length === 0) return NODE_H
  const total = fDomains.reduce((sum, d, i) =>
    sum + domainSubtreeHeight(d, servers, users) + (i > 0 ? GAP_Y : 0), 0)
  return Math.max(total, NODE_H)
}

export function useGraphLayout(
  forests: Forest[],
  domains: Domain[],
  servers: Server[],
  users: User[]
): { nodes: GraphNode[]; edges: GraphEdge[]; viewBox: string } {
  const nodes: GraphNode[] = []
  const edges: GraphEdge[] = []

  let currentY = PADDING

  for (const forest of forests) {
    const fHeight = forestSubtreeHeight(forest, domains, servers, users)

    nodes.push({
      id: `f${forest.id}`,
      label: forest.fqdn,
      type: 'forest',
      x: COL_X[0],
      y: currentY + fHeight / 2 - NODE_H / 2,
      width: NODE_W,
      height: NODE_H,
    })

    const fDomains = domains.filter(d => d.forest_id === forest.id)
    let domainY = currentY

    for (const domain of fDomains) {
      const dHeight = domainSubtreeHeight(domain, servers, users)

      nodes.push({
        id: `d${domain.id}`,
        label: domain.fqdn,
        type: 'domain',
        x: COL_X[1],
        y: domainY + dHeight / 2 - NODE_H / 2,
        width: NODE_W,
        height: NODE_H,
      })
      edges.push({ from: `f${forest.id}`, to: `d${domain.id}` })

      const dServers = servers.filter(s => s.domain_id === domain.id)
      const dUsers   = users.filter(u => u.domain_id === domain.id)
      const uCount   = dUsers.length > 10 ? 1 : dUsers.length

      const serverBlockH = colChildrenHeight(dServers.length)
      const userBlockH   = colChildrenHeight(uCount)

      // Center each column within the domain's vertical range
      let sy = domainY + (dHeight - serverBlockH) / 2
      for (const server of dServers) {
        nodes.push({
          id: `s${server.id}`,
          label: server.fqdn,
          type: 'server',
          meta: { is_dc: server.is_dc },
          x: COL_X[2],
          y: sy,
          width: NODE_W,
          height: NODE_H,
        })
        edges.push({ from: `d${domain.id}`, to: `s${server.id}` })
        sy += NODE_H + GAP_Y
      }

      let uy = domainY + (dHeight - userBlockH) / 2
      if (dUsers.length > 10) {
        nodes.push({
          id: `ua${domain.id}`,
          label: `${dUsers.length} utilisateurs`,
          type: 'user',
          x: COL_X[3],
          y: uy,
          width: NODE_W,
          height: NODE_H,
        })
        edges.push({ from: `d${domain.id}`, to: `ua${domain.id}` })
      } else {
        for (const user of dUsers) {
          nodes.push({
            id: `u${user.id}`,
            label: user.username ?? `#${user.id}`,
            type: 'user',
            x: COL_X[3],
            y: uy,
            width: NODE_W,
            height: NODE_H,
          })
          edges.push({ from: `d${domain.id}`, to: `u${user.id}` })
          uy += NODE_H + GAP_Y
        }
      }

      domainY += dHeight + GAP_Y
    }

    currentY += fHeight + FOREST_GAP
  }

  const maxW = nodes.length ? Math.max(...nodes.map(n => n.x + n.width)) + PADDING : 500
  const maxH = nodes.length ? Math.max(...nodes.map(n => n.y + n.height)) + PADDING : 220

  return { nodes, edges, viewBox: `0 0 ${maxW} ${maxH}` }
}

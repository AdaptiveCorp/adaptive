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

const COL_X = [60, 280, 500, 720]
const NODE_W = 160
const NODE_H = 44
const GAP = 12

export function useGraphLayout(
  forests: Forest[],
  domains: Domain[],
  servers: Server[],
  users: User[]
): { nodes: GraphNode[]; edges: GraphEdge[]; viewBox: string } {
  const nodes: GraphNode[] = []
  const edges: GraphEdge[] = []
  const colY = [0, 0, 0, 0]

  function addNode(
    id: string,
    label: string,
    type: GraphNode['type'],
    col: number,
    meta?: GraphNode['meta']
  ): GraphNode {
    const n: GraphNode = {
      id,
      label,
      type,
      meta,
      x: COL_X[col],
      y: colY[col],
      width: NODE_W,
      height: NODE_H,
    }
    colY[col] += NODE_H + GAP
    nodes.push(n)
    return n
  }

  for (const forest of forests) {
    addNode(`f${forest.id}`, forest.fqdn, 'forest', 0)

    const fDomains = domains.filter((d) => d.forest_id === forest.id)
    for (const domain of fDomains) {
      edges.push({ from: `f${forest.id}`, to: `d${domain.id}` })
      addNode(`d${domain.id}`, domain.fqdn, 'domain', 1)

      const dServers = servers.filter((s) => s.domain_id === domain.id)
      for (const server of dServers) {
        edges.push({ from: `d${domain.id}`, to: `s${server.id}` })
        addNode(`s${server.id}`, server.fqdn, 'server', 2, { is_dc: server.is_dc })
      }

      const dUsers = users.filter((u) => u.domain_id === domain.id)
      if (dUsers.length > 0 && dUsers.length <= 10) {
        for (const user of dUsers) {
          edges.push({ from: `d${domain.id}`, to: `u${user.id}` })
          addNode(`u${user.id}`, user.username ?? `#${user.id}`, 'user', 3)
        }
      } else if (dUsers.length > 10) {
        edges.push({ from: `d${domain.id}`, to: `ua${domain.id}` })
        addNode(`ua${domain.id}`, `${dUsers.length} utilisateurs`, 'user', 3)
      }
    }
  }

  // Center parents vertically on their children
  function centerOn(parentId: string, childIds: string[]) {
    const parent = nodes.find((n) => n.id === parentId)
    const children = nodes.filter((n) => childIds.includes(n.id))
    if (!parent || children.length === 0) return
    const top = Math.min(...children.map((c) => c.y))
    const bot = Math.max(...children.map((c) => c.y + c.height))
    parent.y = (top + bot) / 2 - parent.height / 2
  }

  for (const domain of domains) {
    const dUsers = users.filter((u) => u.domain_id === domain.id)
    const userIds =
      dUsers.length > 0 && dUsers.length <= 10
        ? dUsers.map((u) => `u${u.id}`)
        : dUsers.length > 10
          ? [`ua${domain.id}`]
          : []
    centerOn(`d${domain.id}`, [
      ...servers.filter((s) => s.domain_id === domain.id).map((s) => `s${s.id}`),
      ...userIds,
    ])
  }

  for (const forest of forests) {
    const fDomains = domains.filter((d) => d.forest_id === forest.id)
    centerOn(
      `f${forest.id}`,
      fDomains.map((d) => `d${d.id}`)
    )
  }

  const maxW = nodes.length ? Math.max(...nodes.map((n) => n.x + n.width)) + 60 : 400
  const maxH = nodes.length ? Math.max(...nodes.map((n) => n.y + n.height)) + 40 : 200

  return { nodes, edges, viewBox: `0 0 ${maxW} ${maxH}` }
}

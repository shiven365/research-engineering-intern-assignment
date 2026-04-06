import { useMemo, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'

type GraphData = {
  nodes: any[]
  edges: any[]
}

type Props = {
  graph: GraphData
}

const palette = ['#00d4ff', '#ff6b35', '#7c3aed', '#00ff88', '#ffd166', '#ef476f', '#06d6a0']

export default function NetworkGraph({ graph }: Props) {
  const [selectedNode, setSelectedNode] = useState<any>(null)

  const data = useMemo(
    () => ({
      nodes: graph.nodes.map((n) => ({ ...n, val: Math.log((n.subscribers || 0) + 1) * 3 })),
      links: graph.edges.map((e) => ({ ...e, source: e.source, target: e.target })),
    }),
    [graph],
  )

  if (!graph.nodes.length) {
    return <div style={{ color: 'var(--text-secondary)' }}>No connections found with current filters</div>
  }

  return (
    <div className="split-grid" style={{ height: 520 }}>
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <ForceGraph2D
          graphData={data as any}
          nodeAutoColorBy="community"
          nodeColor={(node: any) => palette[(node.community || 0) % palette.length]}
          linkWidth={(link: any) => Math.sqrt((link.shared_author_count || 1) || 1)}
          onNodeClick={(node: any) => setSelectedNode(node)}
          nodeLabel={(node: any) => `${node.id} (${node.post_count || 0} posts)`}
        />
      </div>
      <div className="card">
        <div className="card-title">Node Details</div>
        {selectedNode ? (
          <div style={{ display: 'grid', gap: 6 }}>
            <div style={{ fontWeight: 700 }}>{selectedNode.id}</div>
            <div>Subscribers: {selectedNode.subscribers}</div>
            <div>Posts: {selectedNode.post_count}</div>
            <div>Avg score: {selectedNode.avg_score}</div>
            <div>PageRank: {selectedNode.pagerank}</div>
            <div>Betweenness: {selectedNode.betweenness}</div>
          </div>
        ) : (
          <div style={{ color: 'var(--text-secondary)' }}>Click a node to inspect.</div>
        )}
      </div>
    </div>
  )
}

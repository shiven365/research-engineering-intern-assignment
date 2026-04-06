import { useState } from 'react'
import Layout from '../components/layout/Layout'
import NetworkGraph from '../components/network/NetworkGraph'
import ErrorState from '../components/ui/ErrorState'
import Skeleton from '../components/ui/Skeleton'
import { useNetwork } from '../hooks/useNetwork'

export default function NetworkPage() {
  const [minEdge, setMinEdge] = useState(1)
  const [metric, setMetric] = useState<'pagerank' | 'betweenness'>('pagerank')
  const [removeNode, setRemoveNode] = useState('')
  const { data, error, loading } = useNetwork(minEdge, metric, removeNode || undefined)

  const removeTop = () => {
    const top = data?.nodes?.[0]?.id
    if (top) setRemoveNode(top)
  }

  return (
    <Layout title="Network">
      <div className="card" style={{ marginBottom: 12, display: 'flex', gap: 12, alignItems: 'center' }}>
        <label>Min edge weight: {minEdge}</label>
        <input type="range" min={1} max={10} value={minEdge} onChange={(e) => setMinEdge(Number(e.target.value))} />
        <select value={metric} onChange={(e) => setMetric(e.target.value as 'pagerank' | 'betweenness')}>
          <option value="pagerank">PageRank</option>
          <option value="betweenness">Betweenness</option>
        </select>
        <button onClick={removeTop}>Remove top node</button>
      </div>
      {loading ? <Skeleton height={450} /> : null}
      {error ? <ErrorState message={error} /> : null}
      {!loading && !error ? <NetworkGraph graph={{ nodes: data?.nodes || [], edges: data?.edges || [] }} /> : null}
    </Layout>
  )
}

import { useState } from 'react'
import { fetchClusters } from '../api/client'
import ClusterMap from '../components/clusters/ClusterMap'
import Layout from '../components/layout/Layout'
import ErrorState from '../components/ui/ErrorState'
import Skeleton from '../components/ui/Skeleton'

export default function ClustersPage() {
  const [nClusters, setNClusters] = useState(8)
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const run = async (nextN = nClusters) => {
    setLoading(true)
    const res = await fetchClusters({ n_clusters: nextN })
    setData(res.data)
    setError(res.error)
    setLoading(false)
  }

  return (
    <Layout title="Topics">
      <div className="card" style={{ marginBottom: 12 }}>
        <label>Cluster count: {nClusters}</label>
        <input
          type="range"
          min={2}
          max={50}
          value={nClusters}
          onChange={(e) => setNClusters(Number(e.target.value))}
          style={{ width: '100%' }}
        />
        <button onClick={() => run()} style={{ marginTop: 10 }}>
          Run clustering
        </button>
      </div>

      {loading ? <Skeleton height={450} /> : null}
      {error ? <ErrorState message={error} /> : null}
      {!loading && !error && data ? (
        <ClusterMap
          coords={data.coords || []}
          labels={data.labels || []}
          titles={data.titles || []}
          subreddits={data.subreddits || []}
          clusterTopics={data.cluster_topics || {}}
        />
      ) : null}
    </Layout>
  )
}

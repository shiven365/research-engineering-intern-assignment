import { useEffect, useState } from 'react'
import { fetchNetwork } from '../api/client'

export function useNetwork(minEdgeWeight = 1, centralityMetric: 'pagerank' | 'betweenness' = 'pagerank', removeNode?: string) {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    fetchNetwork({
      min_edge_weight: minEdgeWeight,
      centrality_metric: centralityMetric,
      remove_node: removeNode,
    })
      .then((res) => {
        if (!mounted) return
        setData(res.data)
        setError(res.error)
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })

    return () => {
      mounted = false
    }
  }, [minEdgeWeight, centralityMetric, removeNode])

  return { data, error, loading }
}

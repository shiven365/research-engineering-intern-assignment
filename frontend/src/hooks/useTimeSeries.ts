import { useEffect, useState } from 'react'
import { fetchTimeSeries } from '../api/client'

export function useTimeSeries(metric = 'post_count', granularity = 'day', subreddit?: string) {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    fetchTimeSeries({ metric, granularity, subreddit })
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
  }, [metric, granularity, subreddit])

  return { data, error, loading }
}

import { useEffect, useState } from 'react'
import { fetchSearch } from '../api/client'

export function useSearch(query: string, k = 10, subreddit?: string) {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const handle = setTimeout(() => {
      setLoading(true)
      fetchSearch({ q: query, k, subreddit })
        .then((res) => {
          setData(res.data)
          setError(res.error)
        })
        .finally(() => setLoading(false))
    }, 300)

    return () => clearTimeout(handle)
  }, [query, k, subreddit])

  return { data, error, loading }
}

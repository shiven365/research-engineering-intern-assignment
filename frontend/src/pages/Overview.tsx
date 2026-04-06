import { useEffect, useState } from 'react'
import { fetchOverview } from '../api/client'
import EngagementChart from '../components/charts/EngagementChart'
import Layout from '../components/layout/Layout'
import ErrorState from '../components/ui/ErrorState'
import Skeleton from '../components/ui/Skeleton'
import StatBadge from '../components/ui/StatBadge'

export default function Overview() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchOverview()
      .then((res) => {
        setData(res.data)
        setError(res.error)
      })
      .finally(() => setLoading(false))
  }, [])

  const chartData = (data?.top_subreddits || []).slice(0, 8).map((s: any) => ({ name: s.subreddit, value: s.post_count }))

  return (
    <Layout title="Overview">
      {loading ? <Skeleton height={200} /> : null}
      {error ? <ErrorState message={error} /> : null}
      {!loading && !error && data ? (
        <div className="stack-md">
          <div className="grid-stats">
            <StatBadge label="Total Posts" value={data.total_posts} />
            <StatBadge label="Unique Authors" value={data.unique_authors} />
            <StatBadge label="Unique Subreddits" value={data.unique_subreddits} />
            <StatBadge label="Date Start" value={data.date_range?.start?.slice(0, 10) || '-'} />
          </div>
          <div className="card animate-in">
            <h3 className="card-title">Top Subreddits by Posts</h3>
            <EngagementChart data={chartData} />
          </div>
        </div>
      ) : null}
    </Layout>
  )
}

import { useState } from 'react'
import AISummaryCard from '../components/charts/AISummaryCard'
import TimeSeriesChart from '../components/charts/TimeSeriesChart'
import Layout from '../components/layout/Layout'
import ErrorState from '../components/ui/ErrorState'
import Skeleton from '../components/ui/Skeleton'
import { useTimeSeries } from '../hooks/useTimeSeries'

export default function Timeline() {
  const [metric, setMetric] = useState('post_count')
  const { data, error, loading } = useTimeSeries(metric, 'day')

  return (
    <Layout title="Timeline">
      <div className="card" style={{ marginBottom: 12 }}>
        <label style={{ marginRight: 8 }}>Metric:</label>
        <select
          value={metric}
          onChange={(e) => setMetric(e.target.value)}
          style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border)' }}
        >
          <option value="post_count">Post Count</option>
          <option value="avg_score">Average Score</option>
          <option value="engagement">Engagement</option>
        </select>
      </div>
      {loading ? <Skeleton height={320} /> : null}
      {error ? <ErrorState message={error} /> : null}
      {!loading && !error ? (
        <div className="card animate-in">
          <TimeSeriesChart data={data?.series || []} />
          <AISummaryCard summary={data?.summary} />
        </div>
      ) : null}
    </Layout>
  )
}

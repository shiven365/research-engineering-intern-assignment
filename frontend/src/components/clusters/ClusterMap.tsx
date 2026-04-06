import {
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

type Props = {
  coords: number[][]
  labels: number[]
  titles: string[]
  subreddits: string[]
  clusterTopics: Record<string, string>
}

const palette = ['#00d4ff', '#ff6b35', '#7c3aed', '#00ff88', '#ffd166', '#ef476f', '#06d6a0', '#999']

export default function ClusterMap({ coords, labels, titles, subreddits, clusterTopics }: Props) {
  if (!coords.length) {
    return <div style={{ color: 'var(--text-secondary)' }}>No clustered data found for current filters.</div>
  }

  const points = coords.map((c, i) => ({
    x: c[0],
    y: c[1],
    cluster: labels[i],
    title: titles[i],
    subreddit: subreddits[i],
  }))

  const byCluster = Array.from(new Set(labels)).map((cluster) => ({
    cluster,
    data: points.filter((p) => p.cluster === cluster),
  }))

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
      <div className="card" style={{ height: 520 }}>
        <ResponsiveContainer>
          <ScatterChart>
            <CartesianGrid stroke="var(--border)" />
            <XAxis dataKey="x" stroke="var(--text-secondary)" />
            <YAxis dataKey="y" stroke="var(--text-secondary)" />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{ background: '#13131f', border: '1px solid #2a2a4a' }}
            />
            <Legend />
            {byCluster.map((clusterObj, i) => (
              <Scatter
                key={String(clusterObj.cluster)}
                name={clusterObj.cluster === -1 ? 'Unclustered' : `Cluster ${clusterObj.cluster}`}
                data={clusterObj.data}
                fill={clusterObj.cluster === -1 ? '#666' : palette[i % palette.length]}
              />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <div className="card">
        <h3 style={{ marginBottom: 10 }}>Cluster Topics</h3>
        <div style={{ display: 'grid', gap: 8 }}>
          {Object.entries(clusterTopics).map(([k, v]) => (
            <div key={k} style={{ border: '1px solid var(--border)', borderRadius: 6, padding: 8 }}>
              <div style={{ fontFamily: 'var(--font-data)', marginBottom: 4 }}>
                {k === '-1' ? 'Unclustered' : `Cluster ${k}`}
              </div>
              <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{v}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

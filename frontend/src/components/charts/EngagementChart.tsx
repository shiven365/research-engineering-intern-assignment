import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

type Props = {
  data: Array<{ name: string; value: number }>
}

const BAR_COLORS = ['#48d8b0', '#6aa2ff', '#83b8ff', '#9ac4ff', '#ffc972', '#ffb454', '#f59b56', '#e88655']

function formatCompact(value: number) {
  return new Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(value)
}

function InsightChip({ label, value }: { label: string; value: string }) {
  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 10,
        padding: '8px 10px',
        background: 'rgba(255,255,255,0.01)',
      }}
    >
      <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>{label}</div>
      <div style={{ fontFamily: 'var(--font-data)', fontSize: 15, color: 'var(--text-primary)' }}>{value}</div>
    </div>
  )
}

function ChartTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const point = payload[0]?.payload
  if (!point) return null

  return (
    <div
      style={{
        background: 'linear-gradient(180deg, rgba(17,29,51,0.96) 0%, rgba(14,24,43,0.96) 100%)',
        border: '1px solid var(--border-bright)',
        borderRadius: 10,
        padding: '10px 12px',
        minWidth: 180,
        boxShadow: '0 10px 24px rgba(0,0,0,0.35)',
      }}
    >
      <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
        #{point.rank} r/{point.name}
      </div>
      <div style={{ marginTop: 4, fontSize: 12, color: 'var(--text-secondary)' }}>
        Posts: <span style={{ color: 'var(--accent-secondary)' }}>{point.value.toLocaleString()}</span>
      </div>
      <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
        Share: <span style={{ color: 'var(--accent-primary)' }}>{point.share.toFixed(1)}%</span>
      </div>
    </div>
  )
}

export default function EngagementChart({ data }: Props) {
  if (!data.length) {
    return <div style={{ color: 'var(--text-secondary)', minHeight: 280 }}>No subreddit data available.</div>
  }

  const ranked = [...data]
    .sort((a, b) => b.value - a.value)
    .map((item, idx) => ({ ...item, rank: idx + 1 }))

  const total = ranked.reduce((sum, row) => sum + row.value, 0)
  const average = total / ranked.length
  const top = ranked[0]
  const top3Share = total ? (ranked.slice(0, 3).reduce((sum, row) => sum + row.value, 0) / total) * 100 : 0

  const chartData = ranked.map((row) => ({
    ...row,
    share: total ? (row.value / total) * 100 : 0,
  }))

  return (
    <div style={{ width: '100%', display: 'grid', gap: 12 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 8 }}>
        <InsightChip label="Top Subreddit" value={`r/${top.name}`} />
        <InsightChip label="Top Volume" value={top.value.toLocaleString()} />
        <InsightChip label="Avg / Subreddit" value={average.toFixed(0)} />
        <InsightChip label="Top-3 Share" value={`${top3Share.toFixed(1)}%`} />
      </div>

      <div style={{ width: '100%', height: 360 }}>
        <ResponsiveContainer>
          <BarChart data={chartData} layout="vertical" margin={{ top: 8, right: 24, bottom: 8, left: 0 }} barCategoryGap={14}>
            <CartesianGrid stroke="var(--border)" strokeDasharray="4 6" horizontal />
            <XAxis
              type="number"
              tickFormatter={formatCompact}
              stroke="var(--text-secondary)"
              axisLine={{ stroke: 'var(--border)' }}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="name"
              width={108}
              stroke="var(--text-secondary)"
              axisLine={false}
              tickLine={false}
            />
            <Tooltip cursor={{ fill: 'rgba(106, 162, 255, 0.08)' }} content={<ChartTooltip />} />
            <ReferenceLine
              x={average}
              stroke="var(--accent-tertiary)"
              strokeDasharray="6 4"
              label={{ value: 'avg', fill: 'var(--text-muted)', fontSize: 11 }}
            />
            <Bar dataKey="value" radius={[0, 10, 10, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={entry.name} fill={BAR_COLORS[index % BAR_COLORS.length]} />
              ))}
              <LabelList dataKey="value" position="right" formatter={(value: number) => value.toLocaleString()} fill="var(--text-secondary)" fontSize={11} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Distribution view of post volume by subreddit. Dashed line marks average volume.</div>
    </div>
  )
}

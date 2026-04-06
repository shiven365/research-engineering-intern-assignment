type Props = {
  summary?: string
}

export default function AISummaryCard({ summary }: Props) {
  return (
    <div className="card" style={{ marginTop: 12, padding: 14 }}>
      <div style={{ fontFamily: 'var(--font-display)', color: 'var(--accent-primary)', marginBottom: 8, fontSize: 14 }}>
        AI Summary
      </div>
      <div style={{ color: 'var(--text-secondary)' }}>{summary || 'No summary available.'}</div>
    </div>
  )
}

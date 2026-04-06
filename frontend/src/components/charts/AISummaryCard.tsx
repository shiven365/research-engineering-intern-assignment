type Props = {
  summary?: string
}

export default function AISummaryCard({ summary }: Props) {
  return (
    <div style={{ marginTop: 12, border: '1px solid var(--border)', borderRadius: 8, padding: 14 }}>
      <div style={{ fontFamily: 'var(--font-display)', color: 'var(--accent-primary)', marginBottom: 8 }}>AI Summary</div>
      <div style={{ color: 'var(--text-secondary)' }}>{summary || 'No summary available.'}</div>
    </div>
  )
}

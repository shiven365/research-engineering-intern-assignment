type Props = {
  response: string
  onSelect: (query: string) => void
}

function parseSuggestions(text: string): string[] {
  const marker = 'FOLLOW-UP QUERIES:'
  const idx = text.indexOf(marker)
  if (idx === -1) return []
  return text
    .slice(idx + marker.length)
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.startsWith('-'))
    .map((line) => line.replace(/^-\s*/, '').trim())
    .slice(0, 3)
}

export default function FollowUpSuggestions({ response, onSelect }: Props) {
  const suggestions = parseSuggestions(response)
  if (!suggestions.length) return null

  return (
    <div style={{ display: 'grid', gap: 8, marginTop: 8 }}>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.6 }}>Ask Next</div>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
      {suggestions.map((s) => (
        <button
          key={s}
          onClick={() => onSelect(s)}
          style={{
            border: '1px solid var(--border-bright)',
            background: 'linear-gradient(180deg, rgba(106,162,255,0.12) 0%, rgba(106,162,255,0.05) 100%)',
            color: 'var(--text-primary)',
            borderRadius: 999,
            padding: '6px 10px',
            cursor: 'pointer',
            fontSize: 12,
          }}
        >
          {s}
        </button>
      ))}
      </div>
    </div>
  )
}

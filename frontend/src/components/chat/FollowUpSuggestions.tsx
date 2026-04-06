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
    <div className="followup-wrap">
      <div className="followup-label">Ask Next</div>
      <div className="followup-list">
      {suggestions.map((s) => (
        <button
          key={s}
          onClick={() => onSelect(s)}
          className="chip-btn"
        >
          {s}
        </button>
      ))}
      </div>
    </div>
  )
}

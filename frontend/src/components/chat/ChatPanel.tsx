import { useState } from 'react'
import { postChat } from '../../api/client'
import FollowUpSuggestions from './FollowUpSuggestions'
import MessageBubble from './MessageBubble'

type Msg = { role: 'user' | 'assistant'; content: string }

type Props = {
  onRetrieved: (posts: any[]) => void
}

export default function ChatPanel({ onRetrieved }: Props) {
  const [history, setHistory] = useState<Msg[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const send = async (forced?: string) => {
    const query = (forced ?? input).trim()
    if (!query) return

    const nextHistory: Msg[] = [...history, { role: 'user', content: query }]
    setHistory(nextHistory)
    setInput('')
    setLoading(true)

    const res = await postChat({ query, history: nextHistory })
    if (res.data?.response) {
      setHistory((prev) => [...prev, { role: 'assistant', content: res.data.response }])
      onRetrieved(res.data.retrieved_posts || [])
    } else {
      setHistory((prev) => [...prev, { role: 'assistant', content: res.error || 'Failed to get AI response.' }])
    }

    setLoading(false)
  }

  return (
    <div className="card" style={{ height: 620, display: 'grid', gridTemplateRows: '1fr auto', gap: 12 }}>
      <div style={{ overflowY: 'auto', display: 'grid', gap: 10, paddingRight: 4 }}>
        {history.map((m, i) => (
          <div key={i}>
            <MessageBubble role={m.role} content={m.content} />
            {m.role === 'assistant' ? <FollowUpSuggestions response={m.content} onSelect={(q) => send(q)} /> : null}
          </div>
        ))}
        {loading ? (
          <div style={{ color: 'var(--text-secondary)', fontSize: 13, padding: '4px 2px' }}>NarrativeScope is analyzing...</div>
        ) : null}
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              send()
            }
          }}
          placeholder="Ask about narrative spread..."
          style={{
            width: '100%',
            minHeight: 70,
            background: 'var(--bg-card)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
            borderRadius: 10,
            padding: 10,
            resize: 'none',
          }}
        />
        <button
          onClick={() => send()}
          disabled={loading}
          style={{
            minWidth: 100,
            borderRadius: 10,
            border: '1px solid var(--accent-primary)',
            background: 'linear-gradient(180deg, rgba(72,216,176,0.22) 0%, rgba(72,216,176,0.12) 100%)',
            color: 'var(--text-primary)',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 600,
          }}
        >
          Send
        </button>
      </div>
    </div>
  )
}

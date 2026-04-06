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
    <div className="card chat-panel">
      <div className="chat-messages">
        {history.map((m, i) => (
          <div key={i}>
            <MessageBubble role={m.role} content={m.content} />
            {m.role === 'assistant' ? <FollowUpSuggestions response={m.content} onSelect={(q) => send(q)} /> : null}
          </div>
        ))}
        {loading ? (
          <div className="chat-loading">NarrativeScope is analyzing...</div>
        ) : null}
      </div>

      <div className="chat-composer">
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
          className="ui-textarea"
        />
        <button
          onClick={() => send()}
          disabled={loading}
          className="btn btn-primary chat-send"
        >
          Send
        </button>
      </div>
    </div>
  )
}

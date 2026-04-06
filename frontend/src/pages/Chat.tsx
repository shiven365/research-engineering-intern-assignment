import { useState } from 'react'
import ChatPanel from '../components/chat/ChatPanel'
import Layout from '../components/layout/Layout'

function toAbsoluteRedditLink(url?: string, permalink?: string) {
  if (url && /^https?:\/\//i.test(url)) return url
  if (url && url.startsWith('/r/')) return `https://www.reddit.com${url}`
  if (permalink && permalink.startsWith('/r/')) return `https://www.reddit.com${permalink}`
  return undefined
}

export default function ChatPage() {
  const [retrieved, setRetrieved] = useState<any[]>([])

  return (
    <Layout title="Intelligence">
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 14 }}>
        <ChatPanel onRetrieved={setRetrieved} />
        <div className="card" style={{ height: 620, overflowY: 'auto' }}>
          <h3 style={{ marginBottom: 10 }}>Recommended Posts</h3>
          {!retrieved.length ? <div style={{ color: 'var(--text-secondary)' }}>No recommendations yet. Ask a question to analyze narrative patterns.</div> : null}
          <div style={{ display: 'grid', gap: 8 }}>
            {retrieved.map((p, i) => (
              <div
                key={`${p.id || p.title}-${i}`}
                style={{
                  border: '1px solid var(--border)',
                  borderRadius: 10,
                  padding: 10,
                  background: 'rgba(255,255,255,0.01)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, alignItems: 'flex-start' }}>
                  <div style={{ fontWeight: 600, lineHeight: 1.4 }}>{p.title}</div>
                  {toAbsoluteRedditLink(p.url, p.permalink) ? (
                    <a
                      href={toAbsoluteRedditLink(p.url, p.permalink)}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        border: '1px solid var(--border-bright)',
                        borderRadius: 999,
                        padding: '4px 10px',
                        fontSize: 12,
                        color: 'var(--accent-primary)',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      Open Post
                    </a>
                  ) : null}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                  r/{p.subreddit} · similarity {Number(p.similarity_score || 0).toFixed(2)} · score {p.score}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  )
}

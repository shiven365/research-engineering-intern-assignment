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
      <div className="chat-layout">
        <ChatPanel onRetrieved={setRetrieved} />
        <div className="card recs-panel">
          <h3 className="card-title">Recommended Posts</h3>
          {!retrieved.length ? <div className="recs-empty">No recommendations yet. Ask a question to analyze narrative patterns.</div> : null}
          <div className="recs-list">
            {retrieved.map((p, i) => (
              <div key={`${p.id || p.title}-${i}`} className="rec-item">
                <div className="rec-item-header">
                  <div className="rec-item-title">{p.title}</div>
                  {toAbsoluteRedditLink(p.url, p.permalink) ? (
                    <a
                      href={toAbsoluteRedditLink(p.url, p.permalink)}
                      target="_blank"
                      rel="noreferrer"
                      className="link-pill"
                    >
                      Open Post
                    </a>
                  ) : null}
                </div>
                <div className="rec-item-meta">
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

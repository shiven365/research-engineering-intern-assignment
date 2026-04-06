type Props = {
  role: 'user' | 'assistant'
  content: string
}

function isLinkToken(token: string) {
  return /^https?:\/\//i.test(token) || token.startsWith('/r/')
}

function toHref(token: string) {
  if (/^https?:\/\//i.test(token)) return token
  if (token.startsWith('/r/')) return `https://www.reddit.com${token}`
  return token
}

function cleanTrailingPunctuation(token: string) {
  return token.replace(/[),.;!?]+$/g, '')
}

function linkify(content: string) {
  const parts = content.split(/(https?:\/\/[^\s]+|\/r\/[^\s]+)/g).filter(Boolean)
  return parts.map((part, idx) => {
    if (!isLinkToken(part)) return <span key={`txt-${idx}`}>{part}</span>
    const clean = cleanTrailingPunctuation(part)
    return (
      <a
        key={`lnk-${idx}`}
        href={toHref(clean)}
        target="_blank"
        rel="noreferrer"
        style={{ color: 'var(--accent-secondary)', textDecoration: 'underline' }}
      >
        {clean}
      </a>
    )
  })
}

export default function MessageBubble({ role, content }: Props) {
  const user = role === 'user'
  return (
    <div style={{ display: 'flex', justifyContent: user ? 'flex-end' : 'flex-start' }}>
      <div
        style={{
          maxWidth: '80%',
          padding: '10px 12px',
          borderRadius: 12,
          background: user
            ? 'linear-gradient(180deg, rgba(72,216,176,0.22) 0%, rgba(72,216,176,0.14) 100%)'
            : 'linear-gradient(180deg, rgba(17,29,51,0.95) 0%, rgba(14,24,43,0.95) 100%)',
          border: `1px solid ${user ? 'var(--accent-primary)' : 'var(--border)'}`,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
          lineHeight: 1.55,
        }}
      >
        {linkify(content)}
      </div>
    </div>
  )
}

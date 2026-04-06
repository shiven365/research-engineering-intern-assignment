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
        className="message-link"
      >
        {clean}
      </a>
    )
  })
}

export default function MessageBubble({ role, content }: Props) {
  const user = role === 'user'
  return (
    <div className={`message-row ${user ? 'user' : 'assistant'}`}>
      <div className={`message-bubble ${user ? 'user' : 'assistant'}`}>
        {linkify(content)}
      </div>
    </div>
  )
}

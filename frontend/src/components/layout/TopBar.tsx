import { Search } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { fetchSearch, fetchSubreddits } from '../../api/client'

type Props = {
  title: string
}

function toAbsoluteRedditLink(url?: string, permalink?: string) {
  if (url && /^https?:\/\//i.test(url)) return url
  if (url && url.startsWith('/r/')) return `https://www.reddit.com${url}`
  if (permalink && permalink.startsWith('/r/')) return `https://www.reddit.com${permalink}`
  return undefined
}

export default function TopBar({ title }: Props) {
  const [query, setQuery] = useState('')
  const [subreddits, setSubreddits] = useState<string[]>([])
  const [selectedSubreddit, setSelectedSubreddit] = useState('')
  const [selectedDate, setSelectedDate] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)
  const [searchMode, setSearchMode] = useState('semantic')
  const [resultCount, setResultCount] = useState(0)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [resultPreview, setResultPreview] = useState<
    Array<{
      id: string
      title: string
      subreddit: string
      date_only?: string
      permalink?: string
      url?: string
    }>
  >([])

  const searchWrapperRef = useRef<HTMLDivElement | null>(null)
  const latestRequestRef = useRef(0)

  const hasSearchContext = useMemo(
    () => Boolean(query.trim() || selectedSubreddit || selectedDate),
    [query, selectedSubreddit, selectedDate]
  )

  useEffect(() => {
    fetchSubreddits().then((res) => {
      const list = (res.data || []).map((s: any) => s.subreddit)
      setSubreddits(list)
    })
  }, [])

  useEffect(() => {
    const closeOnOutsideClick = (event: MouseEvent) => {
      if (!searchWrapperRef.current) return
      if (!searchWrapperRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', closeOnOutsideClick)
    return () => document.removeEventListener('mousedown', closeOnOutsideClick)
  }, [])

  useEffect(() => {
    const handle = setTimeout(() => {
      if (!hasSearchContext) {
        setSearchError(null)
        setSearchMode('semantic')
        setResultCount(0)
        setResultPreview([])
        setIsDropdownOpen(false)
        return
      }

      setIsSearching(true)
      setSearchError(null)
      const requestId = latestRequestRef.current + 1
      latestRequestRef.current = requestId

      fetchSearch({
        q: query,
        k: 5,
        subreddit: selectedSubreddit || undefined,
        start_date: selectedDate || undefined,
        end_date: selectedDate || undefined,
      })
        .then((res) => {
          if (requestId !== latestRequestRef.current) return

          if (res.error) {
            setSearchError(res.error)
            setResultCount(0)
            setResultPreview([])
            setSearchMode('semantic')
            setIsDropdownOpen(true)
            return
          }

          const rows = res.data?.results || []
          const count = rows.length || 0
          const mode = res.data?.mode || 'semantic'

          setResultCount(count)
          setSearchMode(mode)
          setResultPreview(
            rows.slice(0, 5).map((r: any) => ({
              id: r.id,
              title: r.title || 'Untitled post',
              subreddit: r.subreddit || 'unknown',
              date_only: r.date_only,
              permalink: r.permalink,
              url: r.url,
            }))
          )
          setIsDropdownOpen(true)
        })
        .finally(() => {
          if (requestId === latestRequestRef.current) {
            setIsSearching(false)
          }
        })
    }, 300)

    return () => clearTimeout(handle)
  }, [query, selectedSubreddit, selectedDate, hasSearchContext])

  const resetFilters = () => {
    setQuery('')
    setSelectedSubreddit('')
    setSelectedDate('')
    setSearchError(null)
    setSearchMode('semantic')
    setResultCount(0)
    setResultPreview([])
    setIsDropdownOpen(false)
  }

  const statusLine = [
    `${resultCount} result${resultCount === 1 ? '' : 's'}`,
    searchMode,
    selectedSubreddit ? `r/${selectedSubreddit}` : null,
    selectedDate || null,
  ]
    .filter(Boolean)
    .join(' · ')

  return (
    <header
      className="scanline"
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 20,
        backdropFilter: 'blur(8px)',
        background: 'rgba(10,10,15,0.85)',
        borderBottom: '1px solid var(--border)',
        padding: '12px 16px',
      }}
    >
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 1fr', gap: 16, alignItems: 'center' }}>
        <h2 style={{ fontSize: 18 }}>{title}</h2>

        <div ref={searchWrapperRef} style={{ position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: 10, top: 12, color: 'var(--text-muted)' }} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => {
              if (hasSearchContext) setIsDropdownOpen(true)
            }}
            placeholder="Search narratives semantically..."
            style={{
              width: '100%',
              padding: '10px 12px 10px 34px',
              borderRadius: 6,
              border: hasSearchContext ? '1px solid var(--border-bright)' : '1px solid var(--border)',
              background: 'var(--bg-card)',
              color: 'var(--text-primary)',
            }}
          />
          {(isSearching || searchError || (isDropdownOpen && hasSearchContext)) ? (
            <div
              style={{
                position: 'absolute',
                left: 0,
                right: 0,
                top: 'calc(100% + 8px)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                background: 'var(--bg-secondary)',
                boxShadow: '0 12px 30px rgba(0, 0, 0, 0.4)',
                overflow: 'hidden',
                zIndex: 30,
              }}
            >
              <div
                style={{
                  padding: '8px 10px',
                  borderBottom: '1px solid var(--border)',
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  background: 'rgba(255,255,255,0.01)',
                }}
              >
                {isSearching ? 'Searching...' : statusLine || 'No active filters'}
              </div>

              {searchError ? (
                <div style={{ padding: '10px 12px', fontSize: 13, color: 'var(--danger)' }}>
                  {searchError}
                </div>
              ) : null}

              {!isSearching && !searchError && resultPreview.length === 0 ? (
                <div style={{ padding: '10px 12px', fontSize: 13, color: 'var(--text-secondary)' }}>
                  No posts found for the current search filters.
                </div>
              ) : null}

              {!searchError && resultPreview.length > 0 ? (
                <div style={{ maxHeight: 260, overflowY: 'auto' }}>
                  {resultPreview.map((row, index) => (
                    <a
                      key={row.id}
                      href={toAbsoluteRedditLink(row.url, row.permalink) || '#'}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        display: 'block',
                        padding: '9px 10px',
                        borderBottom: index === resultPreview.length - 1 ? 'none' : '1px solid var(--border)',
                        color: 'inherit',
                      }}
                    >
                      <div style={{ fontSize: 13, color: 'var(--text-primary)' }}>{row.title}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>
                        r/{row.subreddit}
                        {row.date_only ? ` · ${row.date_only.slice(0, 10)}` : ''}
                      </div>
                    </a>
                  ))}
                </div>
              ) : null}

              {!isSearching && !searchError && resultCount > resultPreview.length ? (
                <div style={{ padding: '8px 10px', borderTop: '1px solid var(--border)', fontSize: 11, color: 'var(--text-muted)' }}>
                  Showing top {resultPreview.length} of {resultCount} matches.
                </div>
              ) : null}
            </div>
          ) : null}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <select
            value={selectedSubreddit}
            onChange={(e) => setSelectedSubreddit(e.target.value)}
            style={{
              borderRadius: 6,
              border: '1px solid var(--border)',
              background: 'var(--bg-card)',
              color: 'var(--text-primary)',
              padding: '8px 10px',
              width: 180,
            }}
          >
            <option value="">All subreddits</option>
            {subreddits.slice(0, 25).map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            style={{
              borderRadius: 6,
              border: '1px solid var(--border)',
              background: 'var(--bg-card)',
              color: 'var(--text-primary)',
              padding: '8px 10px',
            }}
          />
          <button
            type="button"
            onClick={resetFilters}
            disabled={!hasSearchContext}
            style={{
              borderRadius: 6,
              border: hasSearchContext ? '1px solid var(--border-bright)' : '1px solid var(--border)',
              background: hasSearchContext ? 'rgba(0,212,255,0.08)' : 'var(--bg-card)',
              color: hasSearchContext ? 'var(--accent-primary)' : 'var(--text-muted)',
              padding: '8px 12px',
              cursor: hasSearchContext ? 'pointer' : 'not-allowed',
              fontWeight: 500,
            }}
          >
            Reset
          </button>
        </div>
      </div>
    </header>
  )
}

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
    <header className="topbar scanline">
      <div className="topbar-grid">
        <h2 className="topbar-title">{title}</h2>

        <div ref={searchWrapperRef} className="search-wrap">
          <Search size={16} className="search-icon" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => {
              if (hasSearchContext) setIsDropdownOpen(true)
            }}
            placeholder="Search narratives semantically..."
            className={`ui-input search-input${hasSearchContext ? ' is-active' : ''}`}
          />
          {(isSearching || searchError || (isDropdownOpen && hasSearchContext)) ? (
            <div className="search-dropdown">
              <div className="search-dropdown-header">
                {isSearching ? 'Searching...' : statusLine || 'No active filters'}
              </div>

              {searchError ? (
                <div className="search-dropdown-error">{searchError}</div>
              ) : null}

              {!isSearching && !searchError && resultPreview.length === 0 ? (
                <div className="search-dropdown-empty">
                  No posts found for the current search filters.
                </div>
              ) : null}

              {!searchError && resultPreview.length > 0 ? (
                <div className="search-results">
                  {resultPreview.map((row, index) => (
                    <a
                      key={row.id}
                      href={toAbsoluteRedditLink(row.url, row.permalink) || '#'}
                      target="_blank"
                      rel="noreferrer"
                      className="search-result-item"
                    >
                      <div className="search-result-title">{row.title}</div>
                      <div className="search-result-meta">
                        r/{row.subreddit}
                        {row.date_only ? ` · ${row.date_only.slice(0, 10)}` : ''}
                      </div>
                    </a>
                  ))}
                </div>
              ) : null}

              {!isSearching && !searchError && resultCount > resultPreview.length ? (
                <div className="search-dropdown-footer">
                  Showing top {resultPreview.length} of {resultCount} matches.
                </div>
              ) : null}
            </div>
          ) : null}
        </div>

        <div className="topbar-controls">
          <select
            value={selectedSubreddit}
            onChange={(e) => setSelectedSubreddit(e.target.value)}
            className="ui-select"
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
            className="ui-date"
          />
          <button
            type="button"
            onClick={resetFilters}
            disabled={!hasSearchContext}
            className={`btn btn-ghost${hasSearchContext ? ' is-active' : ''}`}
          >
            Reset
          </button>
        </div>
      </div>
    </header>
  )
}
